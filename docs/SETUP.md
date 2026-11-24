# Setup from scratch

This guide takes you from nothing to a working GK-2A Signal Console. For day-to-day use after that, see the [README](../README.md).

## 1. What you need

| Item | Notes |
|---|---|
| **Dish** | A dish suitable for L-band (GK-2A LRIT is at about 1692 MHz), with a matching feed. A small GOES-style dish setup works for this band |
| **LNA and filter** | A low-noise amplifier with a band-pass filter for 1.69 GHz, mounted close to the feed. Many are powered through the coax ("bias-T"), so check what yours needs |
| **SDR** | The examples use a PlutoSDR. Any SDR that SatDump supports works, with the matching `--source`, gain and sample rate |
| **Coax and adapters** | Short, good-quality cable between feed, LNA and SDR |
| **A PC** | Windows (these instructions), Linux or macOS. Enough CPU for SatDump at 2 Msps |
| **Software** | [SatDump](https://github.com/SatDump/SatDump) (developed against v1.2.2), Python 3.7 or newer, a modern browser |

Antenna and LNA choices are outside this project. Follow your hardware's own instructions, and SatDump's documentation for supported SDRs.

## 2. Point the dish at GK-2A

GK-2A is a geostationary satellite at about **128.2° East**, so it stays at a fixed spot in the sky. Use any satellite pointing calculator or app, enter your position and the satellite longitude, and it gives you the azimuth and elevation. Aim roughly first, then fine-tune using the dashboard (section 7).

If your LNA is powered through the coax, make sure it is actually powered before you expect any signal. As far as I know a PlutoSDR does not supply bias power by itself, so you may need a separate bias-T or power injector. Check your SDR and LNA documentation.

## 3. Install SatDump

1. Download the Windows release from the SatDump GitHub releases page and install or unpack it, for example to `C:\Program Files\SatDump`.
2. Find `satdump.exe`. It is in the `bin` folder, for example `C:\Program Files\SatDump\bin`.
3. Install any driver your SDR needs. For a PlutoSDR, install the Analog Devices PlutoSDR drivers, then check that Windows can see it, for example by opening `http://192.168.2.1` in a browser.
4. Optionally open the SatDump graphical app, choose your SDR as the source and press Start, to confirm the radio opens. Close it again before the next steps, because only one program can hold the SDR at a time.

At start-up SatDump prints errors for radios you do not have, such as `aaronia_sdr_support.dll` or the SDRplay API. These are harmless. The one that matters is `Could not open PlutoSDR device` (or the same for your SDR), which means the radio is not reachable. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 4. Install Python

1. Install Python 3.7 or newer from python.org. On the installer's first screen, tick **Add python.exe to PATH**.
2. In a new PowerShell window, check it works:

```powershell
python --version
```

There is nothing else to install. The bridge uses only the standard library.

## 5. Get the project

Either clone it:

```powershell
git clone https://github.com/User-hX/GOES_gk2A.git
```

or download the ZIP from GitHub and unpack it. You need two files in the same folder: `gk2a_bridge.py` and `gk2a_live.html`.

Folder choices:

- **Easiest:** copy both files into the same folder as `satdump.exe` (the `bin` folder), so the command below works as written.
- **Anywhere else:** keep them together in your own folder and give python the full path to the bridge, for example `python "C:\gk2a\gk2a_bridge.py" --out C:\gk2a_out`. The dashboard is always loaded from the bridge's own folder.

Create the folder where images will be saved, for example `C:\gk2a_out`. SatDump creates it if it is missing.

## 6. First run

Open PowerShell in the folder that holds `satdump.exe`, `gk2a_bridge.py` and `gk2a_live.html`, and run (adjust the source, gain, frequency and sample rate to your station):

```powershell
Start-Process .\satdump.exe -ArgumentList 'live gk2a_lrit C:\gk2a_out --source plutosdr --samplerate 2e6 --frequency 1692.1584e6 --gain 40 --gain_mode 1 --fft_enable --http_server 127.0.0.1:8080' -NoNewWindow; python gk2a_bridge.py --out C:\gk2a_out
```

Then open **http://127.0.0.1:8000** in your browser.

An RTL-SDR example (from this project's original notes, check SatDump's documentation for your device):

```
satdump live gk2a_lrit gk2a_out --source rtlsdr --samplerate 1.024e6 --frequency 1692.14e6 --gain 40 --fft_enable --http_server 127.0.0.1:8080
```

SatDump takes a while to load its plugins, so give it a minute or two. The bridge prints its setup when it starts. Check that it says `(fc: SatDump, span: SatDump)`, which means it read your frequency and sample rate from SatDump. If it says `default`, SatDump had not finished loading yet, and it is re-checked every 5 seconds.

### What a healthy start looks like (no signal yet)

- The pill in the header says SATDUMP LINK (green).
- The banner says SEARCHING, SNR is near 0 and BER is near 0.5.
- The spectrum shows noise. A single thin spike near the centre is usually the SDR itself, not the satellite.
- Reed-Solomon is grey and says "waiting for frame sync".

If the pill says NO LINK TO SATDUMP, SatDump is still loading or has exited. Look at its window.

## 7. Aim and tune

1. Watch the **spectrum** and **SNR** while you move the dish slowly, a little at a time, and pause after each move because the display needs a second to settle.
2. The satellite appears as a **broad bump** above the noise floor. SNR climbs, and the banner changes to SIGNAL FOUND, then VITERBI LOCK, then LOCK · DECODING.
3. Peak the dish for the highest SNR. Try nearby gain values (for example 30 to 50 for a Pluto) and keep the one with the best SNR.
4. Optional: tick **AIM TONE** in Settings. The pitch rises with SNR, so you can aim without looking at the screen.
5. Once locked, each stage of the Receive chain turns green in order: BPSK demodulator, Viterbi, Frame sync, Reed-Solomon.

## 8. Capture images

GK-2A sends a new image roughly every 10 minutes, aligned to UTC. The **Next image downlink** countdown shows the next slot. While you are locked, SatDump decodes the frames and writes the images into `C:\gk2a_out`. The newest one appears in the Decoded image panel, clears itself shortly before the next slot, and has a CLEAR button if you want it gone sooner.

Images can have missing strips if the signal dropped during a scan. A steady lock, with Reed-Solomon not failing, gives complete images.

## 9. Change frequency or sample rate

The dashboard cannot retune the radio. To change either one, stop SatDump, then start it again with a new `--frequency` or `--samplerate`. The bridge reads the new values from the running SatDump within about 5 seconds, and the dashboard follows. To force values instead, pass `--fc` and `--span` (both in MHz) to the bridge.

## 10. Optional: view it from another device

By default the bridge only listens on the PC itself. To open the dashboard from a phone or another computer on your network, start the bridge with `--host 0.0.0.0` and allow Python through the Windows firewall when asked. Then open `http://<PC-address>:8000` from the other device. Do this only on a network you trust, because the bridge has no password.

## 11. Stop and restart

- Press **Ctrl-C** in the window running the bridge.
- Close the SatDump window. If an old SatDump keeps the SDR busy, run `Get-Process satdump* | Stop-Process -Force`.

## 12. Update the project

Download the new files, or run `git pull` if you cloned it, and replace `gk2a_bridge.py` and `gk2a_live.html` together if either is updated.

## 13. Checklist

- [ ] SDR opens in SatDump without errors
- [ ] LNA is powered
- [ ] `python --version` works
- [ ] `gk2a_bridge.py` and `gk2a_live.html` are in the same folder
- [ ] Run command started SatDump with `--fft_enable` and `--http_server 127.0.0.1:8080`
- [ ] Bridge says `(fc: SatDump, span: SatDump)`
- [ ] Dashboard at `http://127.0.0.1:8000` shows SATDUMP LINK and a spectrum
- [ ] Dish pointed at about 128.2° East, SNR rises when peaked
