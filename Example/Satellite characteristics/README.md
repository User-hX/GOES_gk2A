# Evidence of receiving from GK-2A correctly

Besides satellite images, a GK-2A LRIT capture carries extra data files that the Korea Meteorological Administration (KMA) broadcasts on the same link. They come out of SatDump with an `ADD_` prefix (additional-data file class). Their content, language and local times are Korean, which fits GK-2A's korean satellite characteristics and nothing else you would normally receive on this frequency.

## The files and what marks them as Korean

| File | What it is | What makes it Korean |
|---|---|---|
| `ADD_RWW3M_024_20261027_055815_00.gif` | A regional sea-wave forecast map | Titled "KMA Regional Wave Model (ReWW3: 1/30 deg)" with "KIM" in the subtitle (KIM is KMA's Korean Integrated Model). The map is centred on the Korean peninsula and the seas around it, and times are given in UTC and **KST** |
| `ADD_EGMSG_037_20261027_060940_00.txt` | Marine weather warnings, in **Korean** | Written in Hangul, using KMA's warning wording: 풍랑주의보 (wind wave advisory), 발표 / 변경 / 해제 (issued / changed / cancelled), and 해제예고 (cancellation notice) |
| `ADD_EGMSG_037_20261027_060940_00_EN.txt` | The same warnings, in English | A translation of the Korean file, which suggests the Korean text is the original |

## Evidence in the files

1. **Korean issuer.** The maps carry KMA's name and its Korean Integrated Model. The model name (ReWW3) is a KMA product.
2. **Korean language.** The original warning text is Korean. The English file is a translation of it.
3. **Korean place names.** The warnings cover Ulsan, South Gyeongbuk, Jeju Island, the East Sea and the South Sea. These are Korean coastal and offshore zones.
4. **Korean time.** The maps show **KST** (UTC+9) beside UTC. The warning times are local Korean times, and the descriptions use Korean phrasing for the time of day, such as "late afternoon 15:00 to 18:00".
5. **Korean geography.** The regional map is centred on Korea, the Yellow Sea and the East Sea.

Timestamps in the file names are mostly UTC. For example `060940` is 06:09:40 UTC, which is 15:09:40 KST.

## What this does and does not show

This is strong evidence that your station is decoding GK-2A's LRIT broadcast, because the data inside it is KMA's own. The images are centred near GK-2A's longitude of about 128.2° East and with a clean frame sync and Reed-Solomon pass in the dashboard.
