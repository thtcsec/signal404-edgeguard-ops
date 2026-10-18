# EdgeGuard Ops — Hackathon submission overview

**Team:** Signal404  
**Project:** EdgeGuard Ops  
**Competition:** MUGVN Hackathon 2026 — Real-time Operations (MongoDB + Datadog)  
**Baseline commit:** `b0a5b35`  
**Deadline:** 2026-10-31 23:59 ICT  

## One-sentence pitch

EdgeGuard Ops detects thermal throttling on edge AI cameras from MongoDB time-series telemetry, remediates with a commanded safe profile, and proves recovery in Datadog — Detect → Investigate → Respond → Verify.

## Problem

Edge cameras and inference nodes emit continuous telemetry, but operators often learn about thermal throttling only after FPS collapses and frames drop. Network-looking symptoms can mask a thermal root cause. Teams need a closed loop: store high-cardinality device telemetry, detect trends early, act safely, and prove the fleet is healthy again.

## Solution

A .NET 9 + MongoDB + Datadog stack with a Python synthetic fleet simulator:

1. **Detect** — Health analyzer polls MongoDB and uses `$setWindowFields` to compare short vs trailing windows (GPU temp, latency, FPS) while checking that packet loss / network latency stay calm.
2. **Investigate** — Incidents store evidence snapshots and root-cause text; Datadog metrics/logs correlate the same `device_id` / `incident_id`.
3. **Respond** — Response worker polls active incidents, atomically sets `commanded_profile=safe`, and records a remediation action.
4. **Verify** — Recovery requires continuous healthy **reported**-safe telemetry in an observation window (stall/gap resets evidence). Datadog demo monitor returns ALERT → OK when GPU cools.

## Why MongoDB is necessary (not decorative)

| Capability | Role |
| --- | --- |
| Time-series collection (`timestamp` + `metadata`, TTL) | Efficient ingest and retention for per-device samples |
| `$setWindowFields` aggregations | Trend detection without exporting all raw series elsewhere |
| Devices / incidents / remediation collections | Operational state machine for commanded profile and recovery |
| Atomic `$set` on status/profile | Avoid concurrent overwrite of commanded profile during ingest |

Without MongoDB as the system of record, remediations cannot be verified against the same telemetry used for detection.

## Why Datadog is necessary (not decorative)

| Capability | Role |
| --- | --- |
| DogStatsD metrics | Fleet GPU / latency / FPS / active incidents on one timeline |
| Dashboard | Investigate thermal vs network during the demo |
| Monitor (demo + production definitions) | Operator-visible ALERT → OK for the same incident |
| Structured logs | Search `device_id` / `incident_id` / `action_id` |
| APM (Bundle + TCP to Agent) | Prove ingest path is instrumented (see limitations) |

Datadog is the operator lens; MongoDB is the control-plane truth. Both are required for the Detect→Verify story judges expect.

## Architecture (accurate)

```text
Simulator → Telemetry API → MongoDB time-series
                ↓                    ↓
           DogStatsD/logs      Health Analyzer (poll + $setWindowFields)
                ↓                    ↓
           Datadog Agent        Incidents
                                    ↓
                             Response Worker (poll)
                                    ↓
                           commanded_profile=safe
                                    ↓
                     continuous recovery evidence → RESOLVED
```

**Not used:** Kafka, Kubernetes, custom frontend, AI agent, change streams (polling is intentional and implemented).

## Implementation status

### Implemented and tested

- Telemetry ingest; commanded vs reported profile
- Thermal detection via `$setWindowFields`
- Polling remediation + continuous recovery evidence (including stall reset)
- Unit tests: 9 .NET + 6 Python (passing at baseline)
- Datadog Agent Compose profile, DogStatsD, file-tail logs, dashboard/monitor JSON, apply script

### Observed in live Datadog org (2026-10-18)

Evidence: [evidence/live-datadog-validation.json](evidence/live-datadog-validation.json), [evidence/performance-metrics.json](evidence/performance-metrics.json)

- Metrics: `edgeguard.device.gpu_temperature`, `fps`, `inference_latency`
- Logs: remediation / RESOLVED lines; `service:edgeguard-ops`
- Demo monitor ALERT → OK
- Dashboard applied: https://app.datadoghq.com/dashboard/9rr-a4u-2st  
- Monitor: https://app.datadoghq.com/monitors/333934695  
- APM service list: **`edgeguard-telemetry-api` only** (verified)
- E2E incident `inc-thermal-edge-001-20261018085058` → `RESOLVED` / remediation `VERIFIED`

### Limitations (do not over-claim)

- Telemetry is **synthetic**
- Live ALERT demo used **delayed response-worker start** so the monitor could Alert first — not pure autonomous MTTA
- APM cloud verification for **health-analyzer** and **response-worker**: **NOT VERIFIED** (same Bundle wiring; only API service confirmed in Datadog services API)
- No single distributed trace across poll processes (correlation by IDs)
- Transitive NuGet advisories on MongoDB stack (`SharpCompress`, `Snappier`) — classified in checklist

## Demo instructions

See [DEMO.md](DEMO.md), [DEMO_STORYBOARD.md](DEMO_STORYBOARD.md), [DEMO_REHEARSAL.md](DEMO_REHEARSAL.md), [VIDEO_CAPTURE_CHECKLIST.md](VIDEO_CAPTURE_CHECKLIST.md).

## Disclosure

Pre-window scaffold: [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md)  
AI / reuse: [AI_AND_REUSE_DISCLOSURE.md](AI_AND_REUSE_DISCLOSURE.md)

## Official brief (from public organizer materials)

Build a useful MongoDB-powered app; use Datadog to observe, detect, investigate, and resolve an operational challenge end-to-end (incident → recovery). MongoDB expectations include time-series, aggregations/window functions, TTL. Datadog expectations include dashboard + monitor/alert plus at least one of logs / APM / tracing / related Agent capabilities. AI tools allowed if declared. Teams 1–3. Build window through 2026-10-31. Exact online submission form fields may be published by organizers — confirm on the official registration/submission portal before upload.
