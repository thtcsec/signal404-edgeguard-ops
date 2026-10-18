# Video capture checklist (≤3 minutes)

Record in this order. Do **not** show secrets.

## Before record

- [ ] `docker compose up -d mongodb`  
- [ ] `docker compose --profile datadog up -d datadog-agent` (healthy)  
- [ ] `.env` has keys locally; Agent does **not** need `DD_APP_KEY`  
- [ ] Clear Mongo collections or use a fresh incident id  
- [ ] Create `.logs`; absolute `Observability__LogDirectory`  
- [ ] Build Release; `. .\scripts\enable-datadog-dotnet-apm.ps1` for each service  
- [ ] Browser tabs open:  
  - https://app.datadoghq.com/dashboard/9rr-a4u-2st  
  - https://app.datadoghq.com/monitors/333934695  
- [ ] Terminal font large; hide personal paths with keys  

## Capture sequence

| # | Clip | Command / URL | Success look |
| --- | --- | --- | --- |
| 1 | Title / architecture | Slides 1–4 | 15–20s |
| 2 | Start API + analyzer | `dotnet` Release + APM script | `/health` OK |
| 3 | Simulator heat | `EDGEGUARD_SCENARIO=THERMAL_THROTTLE` | `gpu=` rising, `http=202` |
| 4 | Dashboard | Fleet Operations | GPU near/above 85 marker |
| 5 | Mongo incident | `db.incidents.find()` | `status: OPEN` |
| 6 | Wait Alert | Monitor page | **Alert** |
| 7 | Start response-worker | APM script + worker | Logs `commanded_profile=safe` |
| 8 | Recovery | Simulator `reported_profile=safe` | Monitor → **OK**; Mongo `RESOLVED` |
| 9 | Evidence close | Slide 7–8 + optional metrics flash | End on value prop |

## Audio

- Prefer [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md) voice-over, or live mic with same beats.  
- State once: “Worker start delayed for Alert visibility.”

## Export

- 1080p, ≤3:00, no keystrokes revealing `.env`.  
- Keep raw projectors for backup.
