# Configuration

Everything is set on the `gk2a_bridge.py` command line. The bridge passes the values to the dashboard through `/config`, so `gk2a_live.html` needs no editing. Run `python gk2a_bridge.py --help` for the live list.

## Bridge options

| Option | Default | Meaning |
|---|---|---|
| `--out` | required | SatDump output folder, where decoded images are read from |
| `--satdump` | `http://127.0.0.1:8080/api` | SatDump stats URL (match its `--http_server`) |
| `--host` | `127.0.0.1` | address to listen on (`0.0.0.0` for other PCs on the network) |
| `--port` | `8000` | dashboard port |
| `--html` | `gk2a_live.html` | dashboard file, relative to the script |
| `--log-stats` | off | append every SatDump stats reading (numbers only, no FFT) to this file as JSON lines, for diagnosing SNR behaviour |
| `--timeout` | `3.0` | seconds to wait for each SatDump stats request |
| `--hold` | `3.0` | seconds to keep serving the last good stats after a failed request, so brief hiccups do not flash NO LINK (`0` = off) |
| `--fc` | detected, else `1692.1584` | centre frequency in MHz |
| `--span` (or `--bw`) | detected, else `2.0` | spectrum span in MHz, equal to the sample rate |
| `--thr` | `6` | SNR threshold in dB |
| `--avg` | `1` | SNR averaging time in seconds. At 1 or less the display follows the raw reading closely; larger values are steadier but slower |
| `--poll` | `0.25` | how often the dashboard asks for new stats, in seconds. Smaller is livelier but loads SatDump's stats server more |
| `--interval` | `10` | image downlink interval in minutes, aligned to UTC |
| `--clear-before` | `30` | seconds before each expected downlink at which the shown image clears (`0` = never) |
| `--df-tol` | `2000` | largest frequency offset in Hz that counts as green |
| `--ber-max` | `0.3` | BER below this is amber when Viterbi is not locked |
| `--rs-ok` | `8` | average Reed-Solomon errors at or below this is green |
| `--cn-min` | `3` | C/N in dB at or above this is amber when a signal is present |

## Frequency and span come from SatDump

The frequency cannot be retuned while SatDump runs, so the only place you type it is the SatDump command. The bridge:

1. Looks for a running `satdump ... live ...` process, preferring one whose command line mentions `gk2a`.
2. Reads its `--frequency` and `--samplerate` and converts them to MHz.
3. Repeats the check every 5 seconds. The dashboard re-reads `/config` every 5 seconds too, so the spectrum axis follows if you restart SatDump on another frequency. Your threshold and averaging inputs are not overwritten.

Precedence per value: command-line flag (`--fc`, `--span`), then the value detected from SatDump, then the default. The bridge prints the source at start:

```
Setup: fc 1692.1584 MHz | span 2.0000 MHz (fc: SatDump, span: SatDump) | SNR thr 6.0 dB | avg 4.0 s | interval 10 min | clear image 30s before next
```

`default` in the brackets means SatDump was not found (or the bridge started before SatDump finished loading). On Windows the lookup asks PowerShell for `satdump*` processes. On other systems it uses `ps`. A `--samplerate` you leave out of the SatDump command cannot be read, so the span falls back to its default.

## Bridge endpoints

| Address | Purpose |
|---|---|
| `/` | the dashboard page |
| `/config` | setup values, including `src` (where frequency and span came from) |
| `/stats` | SatDump's stats passed through as `{ok, data}`. Adds `stale: true` when serving held data |
| `/latest` | newest `.png` or `.jpg` under the output folder, with the file count and modified time (rescanned at most every 1.5 s) |
| `/img/...` | serves an image from inside the output folder only |

The dashboard polls `/stats` every `--poll` seconds (0.25 by default), `/latest` every 2 s and `/config` every 5 s.

## Link status smoothing

The pill in the header turns red NO LINK when the bridge cannot reach SatDump. Two layers stop a single slow reply from causing a flicker:

- the bridge waits `--timeout` seconds and then serves the last good stats for `--hold` seconds;
- the dashboard shows NO LINK only after 3 failed polls in a row (about 1.5 s).

A real outage is reported after roughly 3 seconds. If your SatDump replies slowly (large FFT replies, busy PC), time it with `curl.exe -s http://127.0.0.1:8080/api` and raise `--timeout` if needed.

## Font size

All text is scaled from one setting, `--fs:1.3`, at the top of the stylesheet in `gk2a_live.html`. Change it (for example `1.2` or `1.5`) and everything follows, including the spectrum labels.
