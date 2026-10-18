# Demo rehearsal runbook

## Reset

```powershell
cd D:\tu_projects\signal404-edgeguard-ops
docker compose up -d mongodb
docker compose --profile datadog up -d datadog-agent
docker exec edgeguard-ops-mongodb-1 mongosh --quiet edgeguard --eval "db.incidents.deleteMany({}); db.telemetry.deleteMany({}); db.devices.deleteMany({}); db.remediation_actions.deleteMany({});"
New-Item -ItemType Directory -Force -Path .logs | Out-Null
Remove-Item .logs\*.log -ErrorAction SilentlyContinue
```

## Staged Alert rehearsal (recommended for video)

1. Terminals: API → analyzer → simulator (`THERMAL_THROTTLE`, Datadog enabled, APM script, absolute log dir).  
2. Watch dashboard + monitor until **Alert** (~2+ minutes of heat for demo monitor).  
3. Start response-worker.  
4. Confirm RESOLVED / VERIFIED / monitor **OK** within ~30–60s after worker start.  
5. Stop all processes; save screenshots if needed.

## Automatic (no Alert staging)

Start API, analyzer, **and** response-worker together before/at simulator start. Incident still remediates; monitor may stay No Data/OK briefly if recovery is faster than `last_2m` evaluation — fine for engineering, weaker for Alert→OK storytelling.

## Timing budget

| Step | Budget |
| --- | --- |
| Heat to Alert (demo monitor) | ~2–3 min off-camera or under B-roll |
| On-camera Alert → worker → OK | ~45–60 s |
| Narration total | ≤ 180 s |

## Failure drills

| Symptom | Fix |
| --- | --- |
| HTTP 500 on ingest | Ensure JsonFileLogger fix is built (baseline `b0a5b35`) |
| No APM | Clear `DD_APM_RECEIVER_SOCKET`; use enable script TCP URL |
| No metrics | `Observability__DatadogEnabled=true`, Agent 8125/udp |
| Monitor No Data | Wait for metric index; confirm `env:development` tags |

Full Datadog env details: [DEMO.md](DEMO.md) section B.
