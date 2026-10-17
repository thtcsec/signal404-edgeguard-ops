# Pre-hackathon baseline

This file is the disclosure record for code that exists before the official MUGVN Hackathon 2026 build window.

## Identity

| Item | Value |
| --- | --- |
| Project | EdgeGuard Ops |
| Team | Signal404 |
| Repository created | 2026-09-30 |
| Official build window | 2026-10-17 to 2026-10-31 (updated by organizers) |
| Scope of this baseline | Project structure, contracts, DTOs, configuration, documentation, and placeholder services |

The scaffold was created before the official build period. It contains only project structure, contracts, DTOs, configuration, documentation, and placeholder services. Core hackathon functionality is implemented during 2026-10-17 to 2026-10-31.

The following are explicitly absent:

- No completed incident detection algorithm exists yet.
- No completed MongoDB analytics exists yet.
- No completed Datadog integration exists yet.
- No completed automated remediation exists yet.

Copying or adapting libraries during the build window still has to be declared in the submission, together with this baseline and any AI coding tools used. The scaffold itself was drafted with Cursor on 2026-09-30.

## Components created before build window

- Repository layout, `.gitignore`, `.editorconfig`, `.env.example`, Docker Compose, and Dockerfiles
- `EdgeGuardOps.sln` and the .NET 9 projects: telemetry API, health analyzer, response worker, shared library, unit tests
- Shared settings for MongoDB and observability, domain records, ingest DTO, repository and worker interfaces
- Metric name and tag constants, `ActivitySource` name constants, and a no-op telemetry sink
- Placeholder implementations that throw `NotSupportedException`
- `GET /health` and `POST /telemetry` returning HTTP 501
- Idle worker loops that log and wait for shutdown
- Python package layout, configuration model, scenario names, and a generator that raises `NotImplementedError`
- Documentation of the intended data model, incident story, and Datadog plan
- Local scripts that start MongoDB, stop Compose, or print that seeding is not implemented

## Components to be implemented during official build window

- MongoDB time-series collection creation with `timeField`, `metaField`, `granularity`, and `expireAfterSeconds`
- Telemetry validation and ingestion into that collection
- Device, incident, and remediation persistence
- Aggregation pipelines and `$setWindowFields` trend comparisons
- Incident detection for the thermal throttling story
- Optional change stream from incidents to the response worker
- Remediation that switches a simulated device to a reduced or safe profile, then verifies recovery
- Deterministic simulator scenarios: `NORMAL`, `THERMAL_THROTTLE`, `NETWORK_DEGRADATION`, `MEMORY_PRESSURE`
- Datadog agent wiring, custom metrics, structured logs, and APM/traces across ingest, analysis, and remediation
- One operational dashboard and at least one monitor, plus the extra Datadog capability used in the demo
- Demo script, video, slides, and the final submission disclosure

Anything implemented on or after 2026-10-17 should stay distinguishable from the pre-window baseline when the submission declares reused work.

## Build-window progress (started 2026-10-17)

Implemented after the official window opened (not part of the pre-hackathon baseline):

- MongoDB.Driver wiring, time-series collection bootstrap with TTL
- Real `POST /telemetry` ingest and device upsert
- Python simulator scenarios that emit synthetic telemetry
- Health analyzer with `$setWindowFields` trend comparison and thermal incident creation
- Response worker safe-profile remediation with observation window before RESOLVED
- Simulator profile sync so remediation is not overwritten by telemetry
