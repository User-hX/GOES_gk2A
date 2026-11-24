# Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `python: can't open file 'gk2a_bridge.py'` | You are in the wrong folder. Change to the folder holding the file, or give python the full path |
| `Start-Process` cannot find the file | `satdump.exe` is in the `bin` folder of the SatDump install (for example `C:\Program Files\SatDump\bin`). Run from there or use its full path |
| Page will not load | The bridge is not running. Look for the `GK-2A bridge on ...` line in its terminal |
| Text error `Cannot read dashboard file` | `gk2a_live.html` is not next to `gk2a_bridge.py` (or `--html` points elsewhere) |
| Page loads but nothing is live | The HTML was opened from disk. Open `http://127.0.0.1:8000` and press Ctrl+F5 |
| NO LINK TO SATDUMP | SatDump is still loading plugins, was not started, or exited. Check its window |
| NO LINK flickers on and off | SatDump's stats server is sometimes slower than 1 second to reply. See "Link status" in [CONFIGURATION.md](CONFIGURATION.md) and time the reply with `curl.exe -s http://127.0.0.1:8080/api` |
| `Could not open PlutoSDR device` | The real fault. Close old SatDump processes (`Get-Process satdump* \| Stop-Process -Force`), other programs using the Pluto (MATLAB, GNU Radio, SDR++) and any WSL `usbipd` attachment. Check that Windows can see the Pluto at `192.168.2.1` |
| `aaronia_sdr_support.dll` or SDRplay API errors | Harmless. Those are drivers for radios you do not use |
| NO FFT DATA | Add `--fft_enable` to the SatDump command |
| Setup line says `default` | SatDump was not found yet. It is re-checked every 5 s, or pass `--fc` and `--span` |
| Everything red, BER near 0.5 | No satellite signal. Peak the dish, check LNA power, try nearby gain values |
| Spectrum has only a thin spike | Probably SDR centre leakage or a stray carrier, not the satellite. The satellite should show as a broad bump |
| Reed-Solomon grey with "waiting for frame sync" | Expected until frame sync locks |
| SNR moves slowly, or swings much more than the SatDump window | Lower the averaging time in Settings (the smallest value is 0.5 s). If the raw reading itself jumps, see "SNR does not match SatDump's window" below |
For a suspected page error, press F12 in the browser, open the Console tab and look for red messages.

## SNR does not match SatDump's window

The dashboard shows the `snr` value from SatDump's stats API, smoothed with a 4 s average by default. SatDump's own window may apply its own smoothing, so the two can differ even when both are correct. To see what the API really sends, sample it directly for about 10 seconds in PowerShell. Several matches per line means more than one `snr` field exists:

```powershell
1..20 | ForEach-Object { (curl.exe -s http://127.0.0.1:8080/api | Select-String -Pattern '"(snr|peak_snr)"\s*:\s*[-0-9.eE+]+' -AllMatches).Matches.Value -join ' | '; Start-Sleep -Milliseconds 500 }
```

Compare those numbers with the window. If the API values jump between near 0 and the signal level while the window stays steady, the window is smoothing them, and a larger averaging time will match it better. If the dashboard feels slow instead, lower the averaging time in Settings.
