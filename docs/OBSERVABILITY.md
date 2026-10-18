# Observability

## Implementation vs live verification

- **Implemented:** DogStatsD `IOperationalTelemetry`, optional Datadog Agent Compose profile, JSON console + **file** logs under `Observability:LogDirectory` (Agent file-tail), `Datadog.Trace.Bundle` automatic instrumentation (CORECLR profiler via `scripts/enable-datadog-dotnet-apm.ps1` or Dockerfiles), reproducible dashboard/monitor JSON, idempotent `scripts/datadog-apply.ps1` (loads `.env`).
- **Verified locally:** Detect → Investigate → Respond → Verify with Datadog disabled (including mid-recovery telemetry stall).
- **Verified live (2026-10-18):** DogStatsD metrics, host file-tail logs, demo monitor ALERT→OK, dashboard apply, APM service `edgeguard-telemetry-api` after forcing TCP (`DD_TRACE_AGENT_URL=http://127.0.0.1:8126`). See [evidence/live-datadog-validation.json](evidence/live-datadog-validation.json).

## Runtime modes

| Mode | Behavior |
| --- | --- |
| `Observability:DatadogEnabled=false` (default) | `NoOpOperationalTelemetry`; no file-tail logs; stack runs without agent |
| `Observability:DatadogEnabled=true` | DogStatsD to agent; JSON console + `.logs/{service}.log`; APM when profiler env is set |

Cross-process polling (API / analyzer / response-worker) is correlated by `device_id`, `incident_id`, and `action_id` in logs and span tags. This repository does **not** claim a single distributed trace across those processes unless W3C/Datadog trace-context propagation is added later.

## Metrics

Emitted by `DogStatsDOperationalTelemetry` (tags include `env:`):

- `edgeguard.device.gpu_temperature`
- `edgeguard.device.inference_latency`
- `edgeguard.device.fps`
- `edgeguard.device.packet_loss`
- `edgeguard.device.*` (cpu/memory/network/dropped frames)
- `edgeguard.incident.active`
- `edgeguard.remediation.count`

## Logs (host → Agent)

Demo runs .NET on the Windows host. Container log collection stays off. Instead:

1. Services write JSON lines to `Observability:LogDirectory` (use an **absolute** path to repo `.logs` for Compose).
2. Compose mounts `./.logs` → `/var/log/edgeguard`.
3. `infrastructure/datadog/conf.d/edgeguard.d/conf.yaml` file-tails `*.log`.

## Traces (.NET automatic instrumentation)

Package: `Datadog.Trace.Bundle` (≥ 3.55.1; patched for CVE-2026-50273 / former NU1903 on &lt; 3.43.0).

`ActivitySource` name: `EdgeGuard.Ops` with spans such as `POST /telemetry`, `HealthAnalyzer.analyze`, `RemediationExecutor.execute`.

**Required:** load the native profiler before process start (`scripts/enable-datadog-dotnet-apm.ps1` on Windows host, or Dockerfile `CORECLR_*` for Compose `apps` profile). A NuGet reference alone does not emit APM spans. Also set `DD_TRACE_ENABLED=true` and `DD_TRACE_OTEL_ENABLED=true` so custom activities are captured.

## Dashboard + monitors

| File | Role |
| --- | --- |
| `dashboard-fleet-operations.json` | Fleet Operations dashboard |
| `monitor-thermal-gpu.json` | **Production-reasonable:** `avg(last_5m)`, `new_group_delay: 60` |
| `monitor-thermal-gpu.demo.json` | **Demo:** `avg(last_2m)`, `new_group_delay: 0` so ALERT can precede recovery |

```powershell
.\scripts\datadog-apply.ps1          # production monitor
.\scripts\datadog-apply.ps1 -Demo    # demo monitor
```

Script loads repo-root `.env` for `DD_API_KEY` / `DD_APP_KEY`, and create-or-updates by title/name (idempotent). No webhook notifications are configured.

## Demo with Datadog

See [DEMO.md](DEMO.md) sections A (verified) and B (live credentials).
