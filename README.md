# GK-2A Signal Console

A browser dashboard for **aiming and monitoring a GK-2A LRIT ground station** running [SatDump](https://github.com/SatDump/SatDump). It shows live signal quality, the SatDump receive chain, a spectrum and the latest decoded image, and its indicators turn **green as the satellite becomes decodable**, much like SatDump's own UI.

![Locked state, rendered with simulated SatDump stats](docs/preview-locked.png)

*Preview rendered with simulated SatDump stats. Searching state: [docs/preview-searching.png](docs/preview-searching.png).*

## Features

- **Live signal readout:** lightly smoothed SNR (about 1 s by default), peak SNR and a 60 s history graph with your threshold line.
- **Receive chain:** BPSK demodulator, Viterbi, frame sync, Reed-Solomon and LRIT products, lighting up one stage at a time as the link comes together.
- **Colour coding:** green means a metric is at a decodable level, amber means marginal, red means failed. Downstream stages stay grey until the stage before them is locked.
- **Spectrum and link tiles:** live FFT with peak offset, plus Δf, BER, RS errors and C/N.
- **Next-downlink countdown:** UTC-aligned, every 10 minutes by default.
- **Decoded image panel:** shows the newest image, clears itself shortly before the next expected downlink, and has a CLEAR button.
- **Aim tone (optional):** pitch follows SNR, with a chime on lock.
- **Setup comes from SatDump:** the bridge reads your frequency and sample rate from the running SatDump command, so you type them once.
- **No dependencies:** Python standard library only, one HTML file, no internet needed.

## How it works

```
SDR -> SatDump (live gk2a_lrit)
         |-> stats API  http://127.0.0.1:8080/api
         |-> decoded images in your output folder
gk2a_bridge.py (port 8000) reads the stats API and the image folder
Browser -> http://127.0.0.1:8000
```

`gk2a_bridge.py` is a small local web server. It serves the dashboard, passes SatDump's stats through, lists the newest image and tells the dashboard your setup values. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Requirements

- [SatDump](https://github.com/SatDump/SatDump) v1.2.2 (developed against this version) with a working GK-2A LRIT setup: SDR, dish and LNA.
- Python 3.7 or newer (developed with 3.11). No packages to install.
- A modern browser.

## Quick start (Windows PowerShell)

Starting from nothing? Follow [docs/SETUP.md](docs/SETUP.md) first.

Put `gk2a_bridge.py` and `gk2a_live.html` in the same folder as `satdump.exe` (or give python the full path to the bridge), then run:

```powershell
Start-Process .\satdump.exe -ArgumentList 'live gk2a_lrit C:\gk2a_out --source plutosdr --samplerate 2e6 --frequency 1692.1584e6 --gain 40 --gain_mode 1 --fft_enable --http_server 127.0.0.1:8080' -NoNewWindow; python gk2a_bridge.py --out C:\gk2a_out
```

Then open **http://127.0.0.1:8000**.

| SatDump argument | Meaning |
|---|---|
| `live gk2a_lrit C:\gk2a_out` | live GK-2A LRIT pipeline, images saved to `C:\gk2a_out` |
| `--source plutosdr` | PlutoSDR input (use your own SDR here) |
| `--samplerate 2e6` | sample rate, which becomes the spectrum span |
| `--frequency 1692.1584e6` | centre frequency in Hz |
| `--gain 40 --gain_mode 1` | gain settings |
| `--fft_enable` | makes SatDump publish spectrum data (needed for the spectrum and C/N) |
| `--http_server 127.0.0.1:8080` | the stats API the bridge reads |

Adjust the source, gain, frequency and sample rate to match your own station. Whatever you pass to SatDump is picked up by the bridge automatically.

### Linux or macOS

```bash
satdump live gk2a_lrit ./gk2a_out --source plutosdr --samplerate 2e6 --frequency 1692.1584e6 --gain 40 --gain_mode 1 --fft_enable --http_server 127.0.0.1:8080 &
python3 gk2a_bridge.py --out ./gk2a_out
```

To stop, press Ctrl-C for the bridge and close SatDump. The frequency cannot be retuned from the dashboard: restart SatDump with a new `--frequency`.

## Documentation

- [docs/SETUP.md](docs/SETUP.md): setting everything up from scratch (hardware, SatDump, Python, first run, aiming).
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md): every bridge option, setup detection, endpoints.
- [docs/DASHBOARD.md](docs/DASHBOARD.md): panels, colour rules, image behaviour, what each metric means.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): common errors and fixes.

## Repository layout

```
gk2a-signal-console/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
├── gk2a_bridge.py        local server linking SatDump and the dashboard
├── gk2a_live.html        the dashboard (single file)
└── docs/
    ├── SETUP.md
    ├── CONFIGURATION.md
    ├── DASHBOARD.md
    ├── TROUBLESHOOTING.md
    ├── preview-locked.png
    └── preview-searching.png
```

## Status and limitations

- Built around SatDump v1.2.2's stats API. The dashboard reads the fields `snr`, `peak_snr`, `freq`, `viterbi_ber`, `viterbi_lock`, `deframer_lock`, `rs_avg` and `fft_values`. If one is missing, its stage shows grey and the banner falls back to your SNR threshold.
- Tested with simulated SatDump stats and in a headless browser. Behaviour on a live GK-2A lock has not been fully verified.
- On Windows the bridge finds SatDump's command line through PowerShell. This was tested only with a stand-in process on Linux, so check that the bridge's startup line says `(fc: SatDump, span: SatDump)`.
- The colour limits (frequency offset, BER, RS errors, C/N) are starting guesses. Tune them from what you see on a real lock.

## Acknowledgements

Built on [SatDump](https://github.com/SatDump/SatDump). This project is not affiliated with or endorsed by SatDump, KMA or GK-2A operators.

## License

MIT. See [LICENSE](LICENSE).
