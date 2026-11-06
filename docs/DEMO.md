# EdgeGuard Ops demo runbook

Current submission: [automatic October 21 walkthrough](submission/MUGVN2026_E2E_WALKTHROUGH.md), [80.1 s video audit](submission/MUGVN2026_VIDEO_AUDIT.md), [non-destructive local review](../README.md#run-locally). October 18 staged monitor evidence below remains historical and separate. Application workers make the automated decisions; Datadog is the operator view.

Detect → Investigate → Respond → Verify Recovery using synthetic telemetry only.

## Verification status

| Path | Status |
| --- | --- |
| Core MongoDB lifecycle (Datadog disabled) | **Verified** locally, including mid-`RECOVERING` simulator stall → observation reset → `RESOLVED` |
| DogStatsD / JSON file logs / Trace.Bundle APM wiring | **Implemented** + live-validated (see below) |
| Datadog Agent Compose + dashboard/monitor JSON + apply script | **Verified** against live org (idempotent apply) |
| Live Datadog UI (metrics, logs, APM, monitor ALERT→OK) | **Verified** 2026-10-18 — evidence: [docs/evidence/live-datadog-validation.json](evidence/live-datadog-validation.json) |

Live URLs (org-specific): dashboard `9rr-a4u-2st`, demo monitor `333934695`.

**Windows host caveat:** do not keep `DD_APM_RECEIVER_SOCKET=/var/run/datadog/apm.socket` in `.env` (from Datadog’s docker-run wizard). That forces Unix sockets and breaks host→Compose APM. `scripts/enable-datadog-dotnet-apm.ps1` clears UDS and uses `http://127.0.0.1:8126`.

## Prerequisites

- Docker Desktop running
- .NET 9 SDK (`%USERPROFILE%\.dotnet\dotnet.exe` if needed)
- Python 3.11+
- Optional Datadog: local `.env` with `DD_API_KEY` + `DD_APP_KEY` (never commit)

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

## B. Datadog-enabled demo — requires live credentials

### B1. Agent + definitions

```powershell
Copy-Item .env.example .env   # fill DD_API_KEY and DD_APP_KEY only locally
New-Item -ItemType Directory -Force -Path .logs | Out-Null
docker compose --profile datadog up -d datadog-agent

# Loads .env automatically; idempotent create/update
.\scripts\datadog-apply.ps1 -Demo
```

`-Demo` applies `monitor-thermal-gpu.demo.json` (`avg(last_2m)`, `new_group_delay: 0`) so ALERT can fire before automated recovery. Production-reasonable settings remain in `monitor-thermal-gpu.json` (`avg(last_5m)`, `new_group_delay: 60`) — apply without `-Demo` for that definition.

### B2. Host process env (each .NET terminal)

Use an **absolute** log directory so the Compose mount `./.logs` receives files:

```powershell
$repo = "D:\tu_projects\signal404-edgeguard-ops"   # adjust if needed
$env:Observability__DatadogEnabled = "true"
$env:Observability__AgentHost = "127.0.0.1"
$env:Observability__LogDirectory = Join-Path $repo ".logs"
$env:Observability__EnvironmentName = "development"
$env:DD_AGENT_HOST = "127.0.0.1"
$env:DD_ENV = "development"
$env:DD_TRACE_ENABLED = "true"
$env:DD_TRACE_OTEL_ENABLED = "true"
$env:DD_LOGS_INJECTION = "true"
```

Enable automatic instrumentation **before** starting each service (after a build so `datadog/` exists under the output folder):

```powershell
& "$env:USERPROFILE\.dotnet\dotnet.exe" build services/telemetry-api -c Release
. .\scripts\enable-datadog-dotnet-apm.ps1 -AppDirectory .\services\telemetry-api\bin\Release\net9.0
$env:DD_SERVICE = "edgeguard-telemetry-api"
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project services/telemetry-api -c Release --no-build
```

Repeat with `health-analyzer` and `response-worker` (set `DD_SERVICE` accordingly).

### B3. Ordering so the demo monitor can ALERT before recovery

Production monitor (`last_5m` + 60s group delay) will not ALERT if remediation cools the device within ~2–3 minutes. For the **demo** monitor:

1. Start Datadog Agent, apply `-Demo` monitor, start API + analyzer + simulator (`THERMAL_THROTTLE`).
2. Wait until GPU stays above 85°C for ~2 minutes and the demo monitor shows **ALERT**.
3. Then start the response worker so remediation → recovery → monitor **OK**.

Do not start the response worker immediately if you need a visible ALERT→OK cycle.

### B4. What to check in Datadog (record observations, not expectations)

1. Metrics: `edgeguard.device.gpu_temperature`
2. Dashboard **EdgeGuard Fleet Operations**
3. Demo monitor ALERT during heat, OK after recovery
4. Logs: service files under `.logs/` and Datadog Log Explorer (`device_id` / `incident_id` / `action_id`)
5. APM: services `edgeguard-telemetry-api`, `edgeguard-health-analyzer`, `edgeguard-response-worker` — spans correlated by IDs (not claimed as one distributed trace)

## C. Evidence checklist

**Verified without Datadog**

- [x] `Observability__DatadogEnabled=false` completes OPEN → MITIGATING → RECOVERING → RESOLVED
- [x] Mid-recovery telemetry stall resets observation; recovery succeeds after telemetry resumes

**Live Datadog org (observed 2026-10-18)**

- [x] Simulator telemetry visible as DogStatsD metrics (`gpu_temperature`, `fps`, `inference_latency`)
- [x] Host `.logs/*.log` appear in Datadog Logs (`service:edgeguard-ops`, remediation/RESOLVED lines)
- [x] APM service `edgeguard-telemetry-api` listed after TCP agent URL fix (analyzer/worker use same Bundle + enable script)
- [x] Dashboard applied: EdgeGuard Fleet Operations
- [x] Demo monitor ALERT → OK during thermal E2E
- [x] E2E incident `RESOLVED` / remediation `VERIFIED`
