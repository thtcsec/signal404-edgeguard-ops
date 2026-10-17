# EdgeGuard Ops demo runbook

Detect → Investigate → Respond → Verify Recovery using synthetic telemetry only.

## Verification status

| Path | Status |
| --- | --- |
| Core MongoDB lifecycle (Datadog disabled) | **Verified** in local E2E, including mid-`RECOVERING` simulator stall → observation reset → successful `RESOLVED` |
| DogStatsD / APM / JSON log wiring in code | **Implemented**; emits only when `Observability__DatadogEnabled=true` and an agent is reachable |
| Datadog Agent Compose profile + dashboard/monitor JSON + apply script | **Implemented** in repo; **not yet applied** to a live Datadog org (needs credentials + separate verification) |
| Live Datadog UI (metrics, dashboard, monitor ALERT→OK, APM) | **Not verified** — do not claim until section B has been run against a real org |

## Prerequisites

- Docker Desktop running
- .NET 9 SDK (`%USERPROFILE%\.dotnet\dotnet.exe` if needed)
- Python 3.11+
- Optional Datadog: `DD_API_KEY`, `DD_APP_KEY`, trial org (section B only)

## A. Core loop (Datadog disabled) — verified

```powershell
.\scripts\dev-up.ps1

# Terminal 1
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project services/telemetry-api

# Terminal 2
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project services/health-analyzer

# Terminal 3
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project services/response-worker

# Terminal 4
cd apps/device-simulator
$env:PYTHONPATH = "src"
$env:EDGEGUARD_TELEMETRY_URL = "http://localhost:5080"
$env:EDGEGUARD_DEVICE_COUNT = "1"
$env:EDGEGUARD_INTERVAL_SECONDS = "1"
$env:EDGEGUARD_SCENARIO = "THERMAL_THROTTLE"
python -m edgeguard_simulator.main
```

Expected MongoDB lifecycle for `edge-001`:

1. Telemetry heats up (`reported_profile=full`)
2. Analyzer opens `OPEN` thermal incident
3. Response worker sets `commanded_profile=safe`, status `MITIGATING`
4. Simulator applies safe and reports `reported_profile=safe`
5. `RECOVERING` with continuous healthy samples for the observation window
6. `RESOLVED` + remediation `VERIFIED`

If the simulator is stopped during `RECOVERING`, observation resets and the incident stays open until continuous evidence returns.

## B. Datadog-enabled demo — pending live credentials

Do **not** treat this section as verified until each checklist item below has been confirmed in a real Datadog org. Keep API/App keys in local `.env` only; never commit them.

```powershell
# .env with DD_API_KEY / DD_APP_KEY (never commit)
docker compose --profile datadog up -d datadog-agent
.\scripts\datadog-apply.ps1

$env:Observability__DatadogEnabled = "true"
$env:Observability__AgentHost = "127.0.0.1"
$env:DD_TRACE_ENABLED = "true"
$env:DD_TRACE_OTEL_ENABLED = "true"
$env:DD_AGENT_HOST = "127.0.0.1"
$env:DD_ENV = "development"
```

Then start the same four terminals as in section A (with env vars set in each .NET terminal).

Expected in Datadog (after live validation):

1. Metrics explorer: `edgeguard.device.gpu_temperature`
2. Dashboard **EdgeGuard Fleet Operations** — GPU, latency, FPS, packet loss, active incidents on one timeline
3. Monitor **EdgeGuard - GPU thermal throttling** — ALERT during heat, OK after recovery
4. Logs: search `incident_id:` / `device_id:` / `action_id:`
5. APM: services `edgeguard-telemetry-api`, `edgeguard-health-analyzer`, `edgeguard-response-worker` — inspect spans tagged with `device.id` / `incident.id` (correlated by IDs; not claimed as one distributed trace)

## C. Evidence checklist

**Verified without Datadog**

- [x] `Observability__DatadogEnabled=false` completes OPEN → MITIGATING → RECOVERING → RESOLVED
- [x] Mid-recovery telemetry stall resets observation; recovery succeeds after telemetry resumes

**Pending live Datadog org**

- [ ] Simulator telemetry visible as DogStatsD metrics
- [ ] Dashboard shows incident + recovery on the same timeline
- [ ] Monitor ALERT → OK
- [ ] Log line contains `incident_id=` matching MongoDB `_id` in Datadog Logs
- [ ] APM shows ingest / analyze / remediate spans (correlated by IDs, not necessarily one distributed trace)
