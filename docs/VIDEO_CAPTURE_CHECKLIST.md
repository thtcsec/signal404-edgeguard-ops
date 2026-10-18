# Video capture checklist (≤3 minutes)

Primary sequence: [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md)  
Narration: [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md)  
Do **not** show secrets. Do **not** delete `docs/evidence/*`.

## Before record

- [ ] `docker compose up -d mongodb`  
- [ ] `docker compose --profile datadog up -d datadog-agent` (healthy)  
- [ ] `.env` has keys locally; Agent does **not** need `DD_APP_KEY`  
- [ ] Clear Mongo collections for a fresh incident **or** keep prior evidence files untouched  
- [ ] Create `.logs`; absolute `Observability__LogDirectory`  
- [ ] Build Release; `. .\scripts\enable-datadog-dotnet-apm.ps1` for each service  
- [ ] Clear `DD_APM_RECEIVER_SOCKET` / use TCP `http://127.0.0.1:8126` on Windows  
- [ ] Browser tabs:  
  - https://app.datadoghq.com/dashboard/9rr-a4u-2st  
  - https://app.datadoghq.com/monitors/333934695  
- [ ] Slides open; terminal font large; hide paths with keys  

## Capture sequence (staged Alert — primary)

| # | Clip | On-screen action | Success look |
| --- | --- | --- | --- |
| 1 | Title / problem | Slides 1–2 | 0:00–0:20 |
| 2 | Architecture | Slide 4 | 0:20–0:45 |
| 3 | Heat | Simulator `THERMAL_THROTTLE` | GPU rising, `http=202` |
| 4 | Dashboard | Fleet Operations | GPU / latency / FPS widgets |
| 5 | Alert + disclosure | Monitor **Alert**; say worker start was delayed | Staged demo stated once |
| 6 | Respond | Start response-worker | `commanded_profile=safe` |
| 7 | Verify | Monitor → **OK**; Mongo `RESOLVED` / `VERIFIED` | If OK lags: show Mongo first, narrate 2m avg |
| 8 | Metrics close | Slide 7–8 | 92.3→54.1 / 177.3→59.6 / 12.1→18.0; safe ≠ 30 FPS |

## Backup clip — automatic E2E

- [ ] Start API + analyzer + **response-worker** together before heat  
- [ ] Record until RESOLVED / VERIFIED  
- [ ] Label: monitor may skip a long Alert if recovery is fast  
- [ ] Optionally add a **new** evidence JSON under `docs/evidence/` — never overwrite existing validation files  

## Audio

- Prefer VI voice-over beats in [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md).  
- State once: “Worker start delayed for Alert visibility.”

## Export

- 1080p, confirm form duration limit (default ≤3:00).  
- No keystrokes revealing `.env`.  
- Keep raw projectors for backup.
