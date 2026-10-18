# EdgeGuard Ops

**Signal404** · real-time observability and automated incident response for IoT and edge AI device fleets.

> Current status: Official build window (17/10 → 31/10). Core Detect → Investigate → Respond → Verify loop is implemented against MongoDB. Datadog integration is wired in-repo (DogStatsD, host log file-tail, .NET APM Bundle) and optional (`Observability__DatadogEnabled=false` by default). Live Datadog org validation is a separate step requiring credentials.

## Problem

Edge cameras and inference nodes report continuously, and operators still find thermal throttling or link degradation after frames are already dropping. EdgeGuard Ops stores that telemetry in MongoDB, surfaces fleet health in Datadog when enabled, and walks one incident from detection through a safe-profile response and a verified recovery.

## Architecture

```text
IoT device simulator
        |
        v
Telemetry API  --------------------->  Datadog (optional)
        |                              DogStatsD / logs / APM
        v
MongoDB Time Series
        |
        v
Health Analyzer (poll)
        |
        v
Incident collection
        |
        v
Response worker (poll)
        |
        v
Safe-profile remediation + recovery evidence
```

Implemented path: simulator → ingest → `$setWindowFields` detection → **poll-based** remediation (not change streams) → continuous recovery evidence → `RESOLVED`. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Hackathon

MUGVN Hackathon 2026, Real-time Operations, with MongoDB and Datadog. Official build window: 2026-10-17 through 2026-10-31. Submission deadline: 2026-10-31 23:59 ICT.

**Submission package**

| Doc | Purpose |
| --- | --- |
| [docs/SUBMISSION.md](docs/SUBMISSION.md) | Overview for judges |
| [docs/JUDGING_MATRIX.md](docs/JUDGING_MATRIX.md) | Creativity / Technical / Impact / Presentation map |
| [docs/IMPACT.md](docs/IMPACT.md) | Measured synthetic outcomes + caveats |
| [docs/FINAL_CHECKLIST.md](docs/FINAL_CHECKLIST.md) | Readiness checklist |
| [docs/DEMO_STORYBOARD.md](docs/DEMO_STORYBOARD.md) | 3-minute storyboard |
| [docs/DEMO_SCRIPT_VI.md](docs/DEMO_SCRIPT_VI.md) | Vietnamese narration |
| [docs/RECORDING_SEQUENCE.md](docs/RECORDING_SEQUENCE.md) | Demo recording sequence + automatic E2E plan |
| [docs/presentation/EdgeGuard-Ops-Judge-Deck.pptx](docs/presentation/EdgeGuard-Ops-Judge-Deck.pptx) | 8-slide judge deck (visual) |
| [docs/evidence/](docs/evidence/) | Live Datadog + performance JSON |

Pre-existing baseline disclosure: [docs/PRE_HACKATHON_BASELINE.md](docs/PRE_HACKATHON_BASELINE.md). AI/reuse: [docs/AI_AND_REUSE_DISCLOSURE.md](docs/AI_AND_REUSE_DISCLOSURE.md).

## Stack

- ASP.NET Core 9 / .NET 9
- MongoDB time-series + TTL + aggregations
- Python 3.11+ synthetic fleet simulator
- Docker Compose (MongoDB; optional Datadog Agent profile)
- Datadog: DogStatsD metrics, Agent file-tail logs, `Datadog.Trace.Bundle` automatic instrumentation

No Kubernetes, Kafka, custom frontend, or AI agent.

## Completed core functionality

| Capability | Status |
| --- | --- |
| Telemetry ingest + commanded vs reported profile | Done |
| Thermal incident detection (`$setWindowFields`) | Done |
| Polling response worker + safe-profile remediation | Done |
| Continuous recovery evidence (stall resets window) | Done |
| Atomic device status / commanded-profile `$set` | Done |
| E2E with Datadog disabled | Verified |
| DogStatsD + Agent Compose + dashboard/monitor JSON | Implemented |
| Host JSON log file-tail into Agent | Implemented |
| .NET APM via Trace.Bundle + profiler env | Implemented (verify spans in live org) |
| Live Datadog UI (metrics / logs / APM API / ALERT→OK) | Observed 2026-10-18 (APM: telemetry-api only) |

## MongoDB usage

Operational store: time-series telemetry (`timestamp` / `metadata`, granularity `seconds`, TTL), plus devices, incidents, and remediation actions. Trend detection uses aggregation + `$setWindowFields`. The response worker **polls** active incidents (change streams remain a future option, not required for the demo).

## Datadog usage

Repo-reproducible dashboard and monitors under `observability/datadog/`, applied with `.\scripts\datadog-apply.ps1` (loads local `.env`). Production monitor uses `avg(last_5m)` + `new_group_delay: 60`; demo monitor is separate (`monitor-thermal-gpu.demo.json`). Details: [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md), [docs/DEMO.md](docs/DEMO.md).

## Incident scenario

[docs/INCIDENT_SCENARIO.md](docs/INCIDENT_SCENARIO.md): thermal throttle → Datadog alert (when live) → MongoDB confirmation → safe profile → recovery → monitor OK / incident `RESOLVED`.

## Layout

| Path | Role |
| --- | --- |
| `services/telemetry-api` | `GET /health`, `POST /telemetry`, device profile API |
| `services/health-analyzer` | Poll + `$setWindowFields` → open thermal incidents |
| `services/response-worker` | Poll incidents → safe profile → verify → `RESOLVED` |
| `shared/EdgeGuard.Shared` | Settings, domain, Mongo, DogStatsD, logging helpers |
| `apps/device-simulator` | Synthetic fleet; `NORMAL` / `THERMAL_THROTTLE` / more |
| `observability/datadog` | Dashboard + production/demo monitor JSON |
| `scripts` | `dev-up`, `datadog-apply`, `enable-datadog-dotnet-apm` |
| `docs` | Design, demo runbook, baseline disclosure |

## Develop

Requirements: .NET 9 SDK (`global.json` selects the 9.x feature band), Python 3.11+, Docker for local MongoDB.

```powershell
& "$env:USERPROFILE\.dotnet\dotnet.exe" build EdgeGuardOps.sln
& "$env:USERPROFILE\.dotnet\dotnet.exe" test EdgeGuardOps.sln
.\scripts\dev-up.ps1
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project services/telemetry-api
```

From `apps/device-simulator`:

```powershell
python -m pip install -r requirements.txt
python -m pytest
$env:PYTHONPATH = "src"
$env:EDGEGUARD_SCENARIO = "THERMAL_THROTTLE"
$env:EDGEGUARD_DEVICE_COUNT = "3"
python -m edgeguard_simulator.main
```

Copy `.env.example` to `.env` only on your machine. Do not commit credentials. Application defaults keep Datadog disabled.
