# Observability

## Implementation vs live verification

- **Implemented in this repo:** DogStatsD `IOperationalTelemetry`, optional Datadog Agent Compose profile, structured JSON logs with `device_id` / `incident_id` / `action_id`, `ActivitySource` spans, reproducible dashboard/monitor JSON, and `scripts/datadog-apply.ps1`.
- **Verified locally:** full Detect → Investigate → Respond → Verify path with `Observability:DatadogEnabled=false` (including mid-recovery telemetry stall).
- **Not yet verified live:** metrics appearing in a Datadog org, dashboard/monitor apply, monitor ALERT → OK in the UI, and APM span capture. Those require `DD_API_KEY` / `DD_APP_KEY` and a separate validation pass — do not claim them until completed.

## Runtime modes

| Mode | Behavior |
| --- | --- |
| `Observability:DatadogEnabled=false` (default) | `NoOpOperationalTelemetry`, stack runs without agent |
| `Observability:DatadogEnabled=true` | DogStatsD metrics to agent; JSON console logs; ActivitySource spans when `DD_TRACE_ENABLED=true` |

Cross-process polling (API / analyzer / response-worker) is correlated by `device_id`, `incident_id`, and `action_id` in logs and span tags. This repository does **not** claim a single distributed trace across those processes unless W3C/Datadog trace-context propagation is added later.

## Metrics

Emitted by `DogStatsDOperationalTelemetry` on ingest / analysis / remediation:

- `edgeguard.device.gpu_temperature`
- `edgeguard.device.inference_latency`
- `edgeguard.device.fps`
- `edgeguard.device.packet_loss`
- `edgeguard.device.*` (cpu/memory/network/dropped frames)
- `edgeguard.incident.active` (gauge of currently active incidents)
- `edgeguard.remediation.count` (increment)

Tags: `device_id`, `site`, `line`, `profile` (reported), `device_type`, `action_type`.

## Traces

`ActivitySource` name: `EdgeGuard.Ops`

Span names:

- `POST /telemetry`
- `TelemetryRepository.insert`
- `HealthAnalyzer.analyze`
- `IncidentRepository.insert`
- `RemediationExecutor.execute`
- `Remediation.incident`

Enable agent capture of custom activities with `DD_TRACE_OTEL_ENABLED=true` and `DD_TRACE_ENABLED=true`.

## Logs

Services use JSON console logging. Search keys in message templates:

- `device_id=`
- `incident_id=`
- `action_id=`
- `commanded_profile=` / `reported_profile=`

## Dashboard + monitor (repo as source of truth)

Definitions live in the repository (reproducible; not UI-only). They are **not applied** until you run the apply script against a Datadog org:

- [dashboard-fleet-operations.json](../observability/datadog/dashboard-fleet-operations.json)
- [monitor-thermal-gpu.json](../observability/datadog/monitor-thermal-gpu.json)

```powershell
$env:DD_API_KEY = "..."   # from local .env — never commit
$env:DD_APP_KEY = "..."
.\scripts\datadog-apply.ps1
```

Thermal monitor **expected** lifecycle after live apply: **ALERT** when GPU avg exceeds 85°C, **OK** after safe-profile recovery brings temperature under the recovery threshold (75°C). Confirm this in the Datadog UI during live validation.

## Demo with Datadog

See [DEMO.md](DEMO.md) sections A (verified) and B (pending live credentials).
