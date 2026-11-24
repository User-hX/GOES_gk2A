# GK-2A Signal Console

A browser dashboard for **aiming and monitoring a GK-2A LRIT ground station** running [SatDump](https://github.com/SatDump/SatDump). It shows live signal quality, the SatDump receive chain, a spectrum and the latest decoded image, and its indicators turn **green as the satellite becomes decodable**, much like SatDump's own UI.


<img width="800" alt="Dashboard in the locked state, all stages green" src="https://github.com/user-attachments/assets/64257870-c756-4496-b3c1-4db0c9bf5113" />


**Preview rendered with simulated SatDump stats. Searching state:** <img width="800" alt="Dashboard in the searching state, no signal" src="https://github.com/user-attachments/assets/bf7d58ae-a678-4805-9576-5e5d2a21a848" />

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

The two files needed are in the repo’s [Dashboard](Dashboard) folder: gk2a_bridge.py and gk2a_live.html. Copy both into the same folder as satdump.exe, then run:
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
- [Dashboard/README.md](Dashboard/README.md): panels, colour rules, image behaviour, what each metric means.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): common errors and fixes.

## Status and limitations

- Built around SatDump v1.2.2's stats API.
- The dashboard reads the fields `snr`, `peak_snr`, `freq`, `viterbi_ber`, `viterbi_lock`, `deframer_lock`, `rs_avg` and `fft_values`. Whichever is missing shows grey and the banner falls back to your SNR threshold.
- The colour limits (frequency offset, BER, RS errors, C/N) are starting guesses. Tune them from what you see on a real lock.

## Acknowledgements

Built on [SatDump](https://github.com/SatDump/SatDump). 
