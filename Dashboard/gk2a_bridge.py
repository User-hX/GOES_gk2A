#!/usr/bin/env python3
"""GK-2A lock-on bridge. Python 3 standard library only.

1) Start SatDump with its stats server, e.g.
   satdump live gk2a_lrit gk2a_out --source rtlsdr --samplerate 1.024e6 \
       --frequency 1692.14e6 --gain 40 --http_server 127.0.0.1:8080
   (check the pipeline id, frequency and sample rate for your SDR in the SatDump docs)

2) Start this bridge (keep gk2a_live.html in the same folder):
   python3 gk2a_bridge.py --out gk2a_out
   It reads --frequency and --samplerate from the running SatDump command line,
   so the dashboard always matches what SatDump was started with. Passing
   --fc / --span (MHz) overrides that. If SatDump isn't found, defaults are used.

3) Open http://127.0.0.1:8000

Everything under "receiver setup" and "quality colouring" is served to the
dashboard at /config, so the HTML needs no editing. Run with --help to list them.
"""
import argparse, json, mimetypes, os, re, subprocess, threading, time, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

ap = argparse.ArgumentParser(description="GK-2A lock-on bridge", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("--satdump", default="http://127.0.0.1:8080/api", help="SatDump stats URL")
ap.add_argument("--out", required=True, help="SatDump output directory")
ap.add_argument("--host", default="127.0.0.1", help="address to listen on (0.0.0.0 for LAN access)")
ap.add_argument("--port", type=int, default=8000)
ap.add_argument("--html", default="gk2a_live.html", help="dashboard file (relative to this script)")

g = ap.add_argument_group("receiver setup (shown in the dashboard)")
g.add_argument("--fc", type=float, default=None, help="centre frequency in MHz (default: read from the running SatDump, else 1692.1584)")
g.add_argument("--span", "--bw", dest="span", type=float, default=None, help="spectrum span / bandwidth in MHz (default: SatDump --samplerate, else 2.0)")
g.add_argument("--thr", type=float, default=6.0, help="SNR threshold in dB")
g.add_argument("--avg", type=float, default=4.0, help="SNR averaging time in seconds")
g.add_argument("--interval", type=float, default=10.0, help="image downlink interval in minutes (UTC aligned)")
g.add_argument("--clear-before", type=float, default=30.0, help="seconds before each expected downlink at which the shown image is cleared (0 = never auto-clear)")

q = ap.add_argument_group("quality colouring (green / amber cut-offs)")
q.add_argument("--df-tol", type=float, default=2000.0, help="max |delta f| in Hz that counts as green")
q.add_argument("--ber-max", type=float, default=0.3, help="Viterbi BER below this is amber when not locked")
q.add_argument("--rs-ok", type=float, default=8.0, help="mean Reed-Solomon errors at or below this is green")
q.add_argument("--cn-min", type=float, default=3.0, help="C/N in dB at or above this is amber before lock")
A = ap.parse_args()

if A.clear_before < 0:
    ap.error("--clear-before must be 0 or more")
for name in ("fc", "span", "avg", "interval"):
    if getattr(A, name) is not None and getattr(A, name) <= 0:
        ap.error("--%s must be greater than 0" % name)

NUM = r"([0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)"


def opt(line, name):
    m = re.search(r"--%s(?:=|\s+)%s" % (name, NUM), line)
    return float(m.group(1)) if m else None


def satdump_cmdlines():
    """Command lines of running 'satdump ... live ...' processes."""
    try:
        if os.name == "nt":
            ps = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'satdump*' } | ForEach-Object { $_.CommandLine }"
            out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                                 capture_output=True, text=True, timeout=10).stdout
            lines = out.splitlines()
        else:
            out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True, timeout=5).stdout
            lines = [l for l in out.splitlines()
                     if os.path.basename(l.strip().split(" ")[0].strip('"')).lower().startswith("satdump")]
    except Exception:
        return []
    return [l for l in lines if re.search(r"\blive\b", l)]


def detect():
    """(fc MHz, span MHz) from the SatDump command line; either may be None."""
    ls = sorted(satdump_cmdlines(), key=lambda l: "gk2a" not in l.lower())
    for l in ls:
        f, s = opt(l, "frequency"), opt(l, "samplerate")
        if f or s:
            return {"fc": round(f / 1e6, 6) if f else None, "span": round(s / 1e6, 6) if s else None}
    return None


DET = {"v": None}


def watch():
    while True:
        time.sleep(5)
        try:
            DET["v"] = detect()
        except Exception:
            DET["v"] = None


def config():
    d = DET["v"] or {}

    def pick(flag, key, default):
        if flag is not None:
            return flag, "flag"
        if d.get(key):
            return d[key], "SatDump"
        return default, "default"

    fc, sf = pick(A.fc, "fc", 1692.1584)
    sp, ss = pick(A.span, "span", 2.0)
    return {"fc": fc, "span": sp, "src": "fc: %s, span: %s" % (sf, ss), "thr": A.thr, "avg": A.avg, "interval": A.interval, "clear": A.clear_before,
            "q": {"df": A.df_tol, "ber": A.ber_max, "rs": A.rs_ok, "cn": A.cn_min}}


HERE = os.path.dirname(os.path.abspath(__file__))
HTML = A.html if os.path.isabs(A.html) else os.path.join(HERE, A.html)
OUT = os.path.abspath(A.out)
EXT = (".png", ".jpg", ".jpeg")
cache = {"t": 0, "v": None}


def latest():
    """Newest image under the SatDump output dir (re-scanned at most every 1.5 s)."""
    if time.time() - cache["t"] < 1.5:
        return cache["v"]
    best, n = None, 0
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.lower().endswith(EXT):
                p = os.path.join(root, f)
                try:
                    m = os.path.getmtime(p)
                except OSError:
                    continue
                n += 1
                if best is None or m > best[0]:
                    best = (m, p)
    v = {"count": n}
    if best:
        v.update(rel=os.path.relpath(best[1], OUT).replace(os.sep, "/"), mtime=best[0])
    cache.update(t=time.time(), v=v)
    return v


class H(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = unquote(urlparse(self.path).path)
        if p == "/":
            try:
                with open(HTML, "rb") as f:
                    return self.send(200, f.read(), "text/html; charset=utf-8")
            except OSError as e:
                return self.send(500, ("Cannot read dashboard file: %s" % e).encode(), "text/plain")
        if p == "/config":
            return self.send(200, json.dumps(config()).encode())
        if p == "/stats":
            try:
                with urllib.request.urlopen(A.satdump, timeout=1) as r:
                    d = json.load(r)
                return self.send(200, json.dumps({"ok": True, "data": d}).encode())
            except Exception as e:
                return self.send(200, json.dumps({"ok": False, "error": str(e)}).encode())
        if p == "/latest":
            return self.send(200, json.dumps(latest()).encode())
        if p.startswith("/img/"):
            f = os.path.abspath(os.path.join(OUT, p[5:]))
            if f.startswith(OUT + os.sep) and os.path.isfile(f) and f.lower().endswith(EXT):
                with open(f, "rb") as fh:
                    return self.send(200, fh.read(), mimetypes.guess_type(f)[0] or "application/octet-stream")
        self.send(404, b"{}")

    def log_message(self, *a):
        pass


print("GK-2A bridge on http://%s:%d  |  SatDump stats: %s  |  images: %s" % (A.host, A.port, A.satdump, OUT))
DET["v"] = detect()
threading.Thread(target=watch, daemon=True).start()
C = config()
print("Setup: fc %.4f MHz | span %.4f MHz (%s) | SNR thr %.1f dB | avg %.1f s | interval %g min | clear image %gs before next" % (C["fc"], C["span"], C["src"], A.thr, A.avg, A.interval, A.clear_before))
if "default" in C["src"]:
    print("Note: no running SatDump command line found for some values, so defaults are used. Start SatDump (it is re-checked every 5 s) or pass --fc / --span.")
print("Colouring: df<=%g Hz | BER<%g | RS<=%g | C/N>=%g dB" % (A.df_tol, A.ber_max, A.rs_ok, A.cn_min))
ThreadingHTTPServer((A.host, A.port), H).serve_forever()
