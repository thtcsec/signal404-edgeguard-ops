# Observability

Plan for Datadog. Nothing in this file is deployed. `Observability:DatadogEnabled` is false in every service, and the Compose file does not start a Datadog agent.

## Metrics

| Name | Kind (planned) |
| --- | --- |
| `edgeguard.device.cpu_usage` | gauge |
| `edgeguard.device.memory_usage` | gauge |
| `edgeguard.device.cpu_temperature` | gauge |
| `edgeguard.device.gpu_temperature` | gauge |
| `edgeguard.device.gpu_usage` | gauge |
| `edgeguard.device.fps` | gauge |
| `edgeguard.device.inference_latency` | gauge |
| `edgeguard.device.packet_loss` | gauge |
| `edgeguard.device.network_latency` | gauge |
| `edgeguard.device.dropped_frames` | gauge or count |
| `edgeguard.incident.active` | gauge |
| `edgeguard.remediation.count` | count |

Constants live in `EdgeGuard.Shared.Observability.MetricNames`. The sink is `NoOpOperationalTelemetry`, which discards samples.

## Tags

`device_id`, `site`, `line`, `device_type`, `profile`, `incident_type`, `severity`.

## Dashboard sections

Plans only, in `observability/datadog/`:

1. Fleet Overview
2. Device Health
3. AI Inference Performance
4. Network Health
5. Active Incidents
6. Incident Investigation
7. Remediation / Recovery

## Monitors to add during the build window

- GPU temperature too high
- Inference latency degradation
- FPS below threshold
- Packet loss above threshold

The thermal demo needs at least one of the first three as the primary alert. Packet loss is the contrast monitor that should stay quiet during that incident.

## Logs and traces

Services already use the standard .NET logger. During the build window, logs should include `device_id`, `incident_id`, and `trace_id` so Datadog Log Management can pivot from the monitor to one device.

`ActivitySource` name: `EdgeGuard.Ops`.

Reserved activity names:

```text
POST /telemetry
    -> TelemetryRepository.insert

HealthAnalyzer.analyze
    -> IncidentRepository.insert
    -> RemediationExecutor.execute
```

No automatic instrumentation package is referenced yet. Expected packages when the trial account is available: Datadog tracing distribution for .NET, and DogStatsD for the custom metrics. Agent configuration belongs in `infrastructure/datadog/`.

## Anomaly detection

Optional. A fixed threshold on GPU temperature plus the MongoDB window comparison is enough for the story. Datadog anomaly detection is a later addition if the trial account and the demo timing allow it.
