# Final demo recording sequence

Total target: **≤ 3:00**. Use staged Alert path for the video; keep a separate automatic E2E for backup evidence.

## A. Staged ALERT path (primary video)

### Setup (off-camera)

1. MongoDB + Datadog Agent healthy.  
2. Clear Mongo collections (optional new run — **do not delete** `docs/evidence/*`).  
3. Absolute log dir; APM enable script; **no** `DD_APM_RECEIVER_SOCKET` on host.  
4. Browser tabs: dashboard `9rr-a4u-2st`, monitor `333934695`.  
5. Slides open to slide 1.

### On-camera actions

| Time | Action on screen | Say (see VI script) |
| --- | --- | --- |
| 0:00–0:20 | Slides 1–2 | Problem |
| 0:20–0:45 | Slide 4 architecture | MongoDB = truth; Datadog = lens |
| 0:45–1:05 | Simulator terminal heating | Live thermal (synthetic) |
| 1:05–1:20 | Datadog dashboard GPU/latency/FPS | Investigate |
| 1:20–1:30 | Monitor shows **Alert** | Explicit disclosure: worker start delayed so Alert is visible |
| 1:30–1:55 | Start response-worker; show log `commanded_profile=safe` | Respond |
| 1:55–2:25 | Monitor → **OK**; Mongo `RESOLVED` | Verify |
| 2:25–2:45 | Slide 7 metric bars | GPU 92.3→54.1, latency 177.3→59.6, FPS 12.1→18.0 — safe mode ≠ 30 FPS |
| 2:45–3:00 | Slide 8 | Close |

### If monitor stays Alert longer than ~60s after recovery

1. Keep camera on dashboard GPU falling under 75°C.  
2. Narrate: “Monitor uses a 2-minute average; OK may lag recovery by up to that window.”  
3. Cut to Mongo `RESOLVED` / remediation `VERIFIED` as hard proof.  
4. Return to monitor when OK appears; if time expires, end on Mongo + metric slide with honest lag note.

## B. Fully automatic E2E (separate clip / backup evidence)

Purpose: prove remediation without intentional delay.

1. Start API + analyzer + **response-worker** together.  
2. Start simulator `THERMAL_THROTTLE`.  
3. Record until RESOLVED / VERIFIED.  
4. Monitor may skip a long Alert if recovery is faster than evaluation — label clip **“automatic closed loop (monitor may not Alert)”**.  
5. Store notes under `docs/evidence/` as a new JSON if you capture timings — **do not overwrite** `live-datadog-validation.json` or `performance-metrics.json`.

## C. Assets already on disk (keep)

- `docs/evidence/live-datadog-validation.json`  
- `docs/evidence/performance-metrics.json`  
- Dashboard / monitor URLs above
