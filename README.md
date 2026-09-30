# EdgeGuard Ops

**Signal404** · real-time observability and automated incident response for IoT and edge AI device fleets.

> Current status: Pre-hackathon scaffold. Core competition functionality has not yet been implemented.

## Problem

Edge cameras and inference nodes report continuously, and operators still find thermal throttling or link degradation after frames are already dropping. EdgeGuard Ops will store that telemetry in MongoDB and show fleet health in Datadog, then walk one incident from detection through a safe-profile response and a verified recovery.

## Architecture

```text
IoT device simulator
        |
        v
Telemetry API
        |
        v
MongoDB Time Series
        |
        +--------------------------+
        |                          |
        v                          v
Health Analyzer              Datadog
        |                 metrics / logs / traces
        v
Incident collection
        |
   change stream (planned)
        |
        v
Response worker
        |
        v
Simulated remediation and recovery telemetry
```

The boxes exist as projects and contracts. The arrows are not implemented. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Hackathon

MUGVN Hackathon 2026, IoT Real-time Operations, with MongoDB and Datadog. Official build window: 2026-10-10 through 2026-10-24. This repository was scaffolded on 2026-09-30 and must be declared as pre-existing baseline. The judged core will be written inside the build window. Disclosure details are in [docs/PRE_HACKATHON_BASELINE.md](docs/PRE_HACKATHON_BASELINE.md).

## Planned stack

- ASP.NET Core 9 / .NET 9
- MongoDB.Driver, added when ingestion starts
- Python 3.11+ simulator
- Docker Compose
- Datadog Agent, APM, logs, and DogStatsD

The demo story is Detect, Investigate, Respond, Verify Recovery. No Kubernetes, Kafka, or custom frontend.

## Planned MongoDB usage

MongoDB will be the operational store. Telemetry will use a time-series collection (`timestamp`, `metadata`, granularity `seconds`, `expireAfterSeconds` from configuration). Devices, incidents, and remediation actions will use regular collections. Trend detection will use an aggregation pipeline and `$setWindowFields`. Change streams are the planned signal into the response worker. The data model is documented in [docs/DATA_MODEL.md](docs/DATA_MODEL.md). Collection creation and the pipeline are not in this scaffold.

## Planned Datadog usage

One fleet-health dashboard, one monitor tied to the thermal incident, plus logs and APM so metrics, logs, and traces explain the same device. Metric names and dashboard sections are listed in [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md). `Observability:DatadogEnabled` is false. No account, dashboard, or monitor is configured.

## Incident scenario

The planned demo, described in [docs/INCIDENT_SCENARIO.md](docs/INCIDENT_SCENARIO.md):

1. A factory camera runs normally.
2. CPU and GPU temperature rise and thermal throttling starts.
3. Inference latency climbs, FPS falls, and dropped frames rise.
4. Datadog alerts, and MongoDB window comparisons confirm the trend.
5. Logs and traces show the cause is thermal, not the network.
6. The response worker switches the device to a safe workload profile.
7. Temperature and latency recover, the monitor returns to OK, and the incident is marked resolved.

None of those steps run today.

## Layout

| Path | Role in this scaffold |
| --- | --- |
| `services/telemetry-api` | `GET /health`, `POST /telemetry` returns 501 |
| `services/health-analyzer` | Idle worker |
| `services/response-worker` | Idle worker |
| `shared/EdgeGuard.Shared` | Settings, records, interfaces, metric names, placeholders |
| `apps/device-simulator` | Models and scenario names; generator raises `NotImplementedError` |
| `observability/datadog` | Written plans, not live monitors |
| `docs` | Design and the pre-hackathon disclosure |

## Develop

Requirements: .NET 9 SDK (`global.json` selects the 9.x feature band), Python 3.11+, Docker if you want local MongoDB. A .NET 10 SDK alone cannot build `net9.0`.

```powershell
dotnet build EdgeGuardOps.sln
dotnet test EdgeGuardOps.sln
.\scripts\dev-up.ps1
dotnet run --project services/telemetry-api
```

From `apps/device-simulator`:

```powershell
python -m pip install -r requirements.txt
python -m pytest
python -m edgeguard_simulator.main
```

The simulator exits with code 2. `.\scripts\seed-placeholder.ps1` writes nothing.

Copy `.env.example` to `.env` only on your machine. Do not commit credentials. Application defaults in `appsettings.json` point at `mongodb://localhost:27017` and keep Datadog disabled.
