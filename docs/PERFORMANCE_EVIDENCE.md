# Performance evidence (synthetic incident)

**Do not present as production results.**

## Incident under analysis

| Field | Value |
| --- | --- |
| Incident | `inc-thermal-edge-001-20261018085058` |
| Remediation | `act-safe-edge-001-20261018085250` |
| Device | `edge-001` |
| Machine-readable | [evidence/performance-metrics.json](evidence/performance-metrics.json) |
| Datadog companion | [evidence/live-datadog-validation.json](evidence/live-datadog-validation.json) |

## Timestamps (UTC)

| Event | Timestamp |
| --- | --- |
| First telemetry | 2026-10-18T08:50:17.829Z |
| Detected | 2026-10-18T08:50:58.764Z |
| Remediation requested | 2026-10-18T08:52:50.208Z |
| Remediation verified / resolved | 2026-10-18T08:53:08.45Z |

## Computed intervals

| Interval | Seconds | Notes |
| --- | --- | --- |
| Detection latency (first sample → detect) | **40.9** | Polling analyzer + windows |
| Detection → remediation request | **111.4** | **STAGED** — response-worker delayed for Datadog ALERT |
| Remediation → verified | **18.2** | Continuous recovery evidence (~15s observation) |
| Detection → resolved | **129.7** | Staged end-to-end |

## Metric deltas (MongoDB averages)

| Signal | Before detection window | After resolve (`safe`) |
| --- | --- | --- |
| GPU °C | 92.3 | 54.1 |
| Inference latency ms | 177.3 | 59.6 |
| FPS | 12.1 | 18.0 |

Incident document evidence at open: GPU 85.1°C, latency 136.0 ms, FPS 17.4 (1m analyzer window averages).

## NOT VERIFIED

- Autonomous detect→remediate latency with worker already running (would be shorter; not re-measured in the staged Alert run).
- APM span counts for analyzer/response-worker in Datadog.
- Multi-device concurrent incident metrics.
