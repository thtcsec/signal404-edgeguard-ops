# EdgeGuard Ops editorial QA — 2026-10-21

Overall: **PASS with recording limits stated below.** Backend was not rewritten. Automatic E2E `20261021202014` is the run shown in the video. Prior passed run `20261021183352` is preserved on disk.

## Video

`docs/video/edgeguard-ops-final-demo.mp4` (local, gitignored)

- H.264 1920×1080, **90.1 s**, silent AAC (`anullsrc`), no TTS, no voiceover
- Timeline-aligned English SRT burned in (`docs/video/edgeguard-ops-subtitles.srt`)
- Structure: **Inject Fault → Detect → Respond → Verify**
- Backup of the previous 72 s cut: `docs/video/edgeguard-ops-final-demo.pre-editorial-rebuild.mp4`

| Beat | Footage | On-screen evidence |
| --- | --- | --- |
| Inject 3.2–62.2 s | Live classic **conhost** `THERMAL_THROTTLE` from empty `devices` (first commanded profile **full**) | gpu 65.6°C / 29 FPS / profile=full → 85°C+ degraded → commanded_profile=safe ~54°C / 18 FPS |
| Detect 62.2–75.2 s | Playwright Datadog, paused **3 m** window 20:19–20:23 local | Time picker `Oct 21, 8:19 pm – 8:23 pm`; log `inc-thermal-edge-001-20261021132057` RESOLVED |
| Respond 75.2–83.0 s | 16:9 conhost of this run’s worker log | **Remediation applied** `act-safe-edge-001-20261021132102` then **Incident RESOLVED** |
| Verify 83.0–86.9 s | Live `mongosh` of latest docs | incident RESOLVED, action VERIFIED, `devices.findOne({_id:'edge-001'}).profile=safe` |

## E2E evidence (this video)

`docs/evidence/e2e-verified-20261021202014.json` **PASSED**

- incident `inc-thermal-edge-001-20261021132057` detected 13:20:57Z, resolved 13:21:27Z
- remediation `act-safe-edge-001-20261021132102` **VERIFIED**
- device `_id=edge-001` profile=safe
- Preserved earlier passed run: `docs/evidence/e2e-verified-20261021183352.json`

## Quality gates

- QA frames every 5 s and at scene cuts: `docs/video/preview-frames/editorial-qa-01.png` … plus `-mobile.png` at 854×480
- Captions are burned in; timing matches the visible beat after a crop so newest simulator rows (safe recovery) stay on screen
- FFmpeg `freezedetect n=0.003:d=2` long intervals (>4 s):
  - 24.2–36.6 s — live simulator console (text updates on a black field; few pixels change)
  - 63.4–73.6 s — paused Datadog 3-minute historical window (graphs do not tick)
- No 18:28 / 18:29 monitor ALERT and no 18:35 overlay. This cut is **20:20 local / 13:20 UTC**.

## Recording method

- OBS Studio is **not installed**
- Windows Terminal title-grab records a **black** frame
- `Start-Process ffmpeg -ArgumentList` splits `title=EG Inject Fault` at spaces (`Can't find window 'EG'`) — titles without spaces plus in-process splat (`gdigrab-title.ps1`) are required
- Working method: **classic `conhost.exe` + ffmpeg `gdigrab` by title**, scaled/cropped to 16:9

## Limits (explicit)

1. Datadog **GPU temperature** timeseries in the 3-minute window rises from ~64°C and stays below the drawn 85°C marker (~80°C visual peak). The **simulator console and analyzer log** for this same run show GPU **95°C** / gpu1m **86.3°C**. Do not read the timeseries peak as 95°C. Likely DogStatsD gauge averaging vs per-sample console lines.
2. Datadog **GPU now 74.1°C / FPS now 15** query-value widgets do **not** match recovered Mongo telemetry (gpu 54.7, fps 18). Those widgets appear to follow live agent data, not the paused window. The timeseries, incident bars, and log line are the windowed evidence.
3. Datadog **Add Widgets** leftover tile is cosmetic editor chrome, not an application defect.
4. Playwright’s recorded tab has a grey strip along the bottom of the dashboard clip; captions sit in that strip and do not cover the log line or time picker.
5. Respond console is a paced replay of the authentic worker log from this run (the live worker JSON window is unreadable). Inject and Mongo are live windows.
6. A first same-day recapture (`20261021201508`) closed the loop from full but ffmpeg never grabbed the window (title split). Evidence for that run is kept; it is **not** the video.

## Verdict

**PASS** for a silent, captioned, 16:9 judge demo of a real automatic E2E from healthy/full, with the Datadog and encoding limits above. Not a backend change.
