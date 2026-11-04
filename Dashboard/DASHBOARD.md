# Dashboard guide

## Layout

- **Header:** title, uptime, UTC clock and the SATDUMP LINK pill (red NO LINK when the bridge cannot reach SatDump).
- **Left column:**
  - *Next image downlink:* countdown to the next UTC-aligned slot, with `every 10 min · next HH:MM` on one line. Turns amber in the last 30 s.
  - *Session:* LOCKS (acquisitions since the page opened), THIS LOCK and BEST LOCK in seconds, and IMAGES (all image files in the output folder).
  - *Settings:* centre frequency, span and interval are read-only and come from the bridge. SNR threshold and averaging time are editable. AIM TONE plays a pitch that rises with SNR and a chime on lock.
  - *Event log:* lock events, stage changes, setup, new and cleared images.
- **Centre:** the decoded image with a CLEAR button.
- **Right column:** *Signal* (stage banner, peak and smoothed SNR, 60 s history), *Spectrum* (live FFT with peak frequency and offset) and *Link* (Δf, BER, RS ERR, C/N).
- **Bottom:** *Receive chain* with BPSK demodulator, Viterbi decoder, frame sync, Reed-Solomon and LRIT products.

## Averaging time and threshold

On every poll (0.25 s by default) the dashboard applies an exponential moving average to the raw SNR, with the averaging time (default 1 s) as its time constant. With an averaging time above 1 s it also takes the median of the last 3 readings first, to remove single-reading spikes. A larger value is steadier but slower: a step change is about 63 percent reflected after one averaging time. Set it to 0.1 to 0.5 for a near-raw display.

The smoothed SNR drives the big SNR number, the history graph, the aim tone pitch, the SIGNAL FOUND stage, the SNR and BPSK colours, and the lock decision only when SatDump reports no lock stats. It does not affect raw SNR, peak SNR, Δf, BER, RS, C/N or the lock flags, which are instantaneous. The spectrum has its own light, fixed smoothing, and its peak-hold line falls at a fixed rate in dB per second.

The SNR threshold normally does not decide lock, because SatDump reports its own lock flags. It sets the dashed line on the graph and the green boundary for SNR and peak SNR.

## Stage banner

| Banner | Colour | Condition |
|---|---|---|
| LOCK · DECODING | green | frame sync locked (falls back to Viterbi lock, then SNR at or above threshold, if a stat is missing) |
| VITERBI LOCK · SYNCING | amber | Viterbi locked, frame sync not yet |
| SIGNAL FOUND · FINE-TUNE | amber | smoothed SNR at or above threshold, no lock |
| SEARCHING | red | signal below threshold |
| WAITING FOR PIPELINE | amber | SatDump reachable but no SNR yet |
| NO LINK TO SATDUMP | red | stats API unreachable |

## Colour coding

Each metric is coloured on its own. Green means that metric is at a decodable level. The banner and chain turn green only on a real lock, and nothing downstream goes green or amber before the stage in front of it.

| Item | Green | Amber | Other |
|---|---|---|---|
| SNR and peak SNR | at or above threshold | within 3 dB below | neutral |
| Δf | signal present and within the limit (2 kHz) | signal present but off | neutral with no signal |
| BER | Viterbi locked | below 0.3 but not locked | neutral |
| RS ERR | average 8 or less, once frame sync is locked | 8 to 16 | red FAIL; grey until frame sync locks |
| C/N | locked | at or above 3 dB while smoothed SNR is within 3 dB of the threshold | neutral |
| BPSK node | SNR at or above threshold | WEAK, within 3 dB | grey |
| Viterbi node | LOCK | none | red NO LOCK |
| Frame sync node | SYNC | none | red HUNTING |
| Reed-Solomon node | PASS | WEAK | red FAIL; grey "waiting for frame sync" before lock |
| LRIT products node | RX while an image is shown | none | grey, waiting |

The spectrum trace, its peak label and the THIS LOCK tile also turn green while locked. Peak SNR looks like a running maximum, so it stays green once seen.

Reed-Solomon is gated on frame sync because SatDump reports `0.0` errors before any data has reached that stage, which would otherwise read as a pass.

## Image handling

- A new image appears as soon as SatDump writes it, and the log says NEW IMAGE DECODED.
- The image clears automatically `--clear-before` seconds (default 30) before each expected downlink, and the panel says WAITING FOR NEXT IMAGE. An image from an earlier cycle stays hidden after a page reload.
- CLEAR removes the current image immediately. The next new image shows again.
- The LRIT PRODUCTS node is green only while an image is on display, showing the capture time and file name. It returns to grey when the image clears, by timer or by button.

## What the link metrics mean

- **Δf:** the demodulator's frequency offset in Hz. Only meaningful when a signal is present, otherwise it just wanders.
- **BER:** bit error rate seen by the Viterbi decoder. Noise gives about 0.5, a good lock gives a small number.
- **RS ERR:** Reed-Solomon fixes damaged bytes. Each codeword can fix up to 16 bad bytes and LRIT uses 4 in parallel. The tile shows the average bytes fixed per codeword, so lower is better. FAIL means a codeword could not be repaired, so that data is lost and the image gets gaps.
- **C/N:** the dashboard's own rough estimate, the strongest spectrum peak above the median noise floor in dB. It is not SatDump's SNR and is not calibrated, so compare it only with itself. It needs FFT data, and a thin spike such as SDR centre leakage can inflate it. A real signal should appear as a broad bump above the noise, not a single thin line.
