# EdgeGuard Ops final QA — silent polish 2026-10-21

Overall: **PASS with recording limits stated below.** E2E `20261021183352` is unchanged. This pass is video-only.

## Video

`docs/video/edgeguard-ops-final-demo.mp4` (local, gitignored)

- H.264 1920×1080, **72 s**, silent AAC, no voiceover, no burned-in subtitles
- Structure on screen: **Inject Fault → Detect → Respond → Verify**
- Backup of the previous longer cut: `docs/video/edgeguard-ops-final-demo.vo-backup.mp4`

| Beat | Footage | Caption |
| --- | --- | --- |
| Inject | Classic **conhost** live start of `python -m edgeguard_simulator.main` with `THERMAL_THROTTLE` | Same command as E2E 20261021183352 |
| Detect | One loaded Datadog dashboard pass (spinners trimmed) | E2E **18:35**, not the 18:29 prior attempt |
| Respond | Crop of logs + GPU now + FPS now | `Incident RESOLVED` …`20261021113510`, FPS 18 |
| Verify | Classic **conhost** live `mongosh` `findOne` of that incident / action / `_id=edge-001` plus worker RESOLVED lines | profile=safe, VERIFIED |

No dashboard clip is reused to pad duration. Monitor Event Timeline (18:29 ALERT) is **not** in this cut.

## E2E evidence (preserved)

`docs/evidence/e2e-verified-20261021183352.json`

- incident `inc-thermal-edge-001-20261021113510` **RESOLVED**
- remediation `act-safe-edge-001-20261021113514` **VERIFIED**
- `db.devices.findOne({_id:"edge-001"})` **profile=safe**
- telemetry **profile=safe**

## Recording method

- OBS Studio is **not installed**.
- Windows Terminal `gdigrab` by title records a **black** frame.
- Full-desktop `gdigrab` captured unrelated apps (YouTube / Instagram) and was excluded.
- Working method: **classic `conhost.exe` + ffmpeg `gdigrab` by window title**, scaled to even 1920×1080.

## Limits (explicit)

1. The inject recapture is a **live start** of the same simulator command. Commanded profile is still **safe** from the E2E, so this recapture’s console lines stay ~54°C / FPS 18. It does **not** re-fire a thermal incident. Datadog graphs are the original 18:35 E2E.
2. Datadog “Add Widgets” editor tile is still visible on full-frame dashboard shots (cosmetic, not a data defect).
3. Verify console is genuine `docker exec mongosh` + `Select-String` on the saved worker log; the window is mostly static after the commands finish.

## QA frames

`docs/video/preview-frames/silent-qa-01.png` … `silent-qa-07.png` — title, live simulator, loaded Datadog, RESOLVED crop, mongosh VERIFIED / profile=safe.
