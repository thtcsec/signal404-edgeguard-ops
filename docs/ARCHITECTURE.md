# Architecture

EdgeGuard Ops is a single-developer system: one ingest API, two workers, one database, one simulator, and Datadog as the operator view. This document describes the target. The scaffold only contains the process boundaries and contracts.

## Runtime pieces

| Piece | Technology | Scaffold behavior |
| --- | --- | --- |
| Device simulator | Python 3.11 | Exits without sending samples |
| Telemetry API | ASP.NET Core 9 | Health check and HTTP 501 ingest |
| Health analyzer | .NET worker | Logs and idles |
| Response worker | .NET worker | Logs and idles |
| Operational store | MongoDB 8 | Container only; no collections are created |
| Observability | Datadog | Documented integration points; disabled in configuration |

## Planned request path

```text
POST /telemetry
    -> Telemetry API
    -> validation
    -> TelemetryRepository.insert
    -> MongoDB time-series collection
```

Trace activity names reserved for that path are `POST /telemetry` and `TelemetryRepository.insert` (`EdgeGuard.Shared.Observability.TraceSources`). The API does not start those activities yet.

## Planned detection and response path

```text
HealthAnalyzer.analyze
    -> aggregation + $setWindowFields
    -> IncidentRepository.insert
    -> incidents collection
    -> change stream
    -> RemediationExecutor.execute
    -> simulator profile change
    -> recovery samples
```

The analyzer does not call `IFleetHealthAnalyzer.AnalyzeAsync`, because the registered implementation is a placeholder that throws. The response worker likewise does not call `IRemediationExecutor`.

## Why these boundaries

The incident story needs a writer (simulator and API), a store (MongoDB), a decision loop (analyzer), an action loop (response worker), and an outside view (Datadog). Splitting those four code projects keeps the demo explainable without a message bus. The simulator posts HTTP directly to the API. Workers read and write MongoDB. Datadog receives metrics, logs, and traces from the same processes.

## Configuration

`MongoDb` and `Observability` sections are the shared configuration objects. Defaults target local MongoDB and set `DatadogEnabled` to false. Environment variables use the ASP.NET `__` form, for example `MongoDb__ConnectionString`.

## Deployment shape for the hackathon

`docker compose up` starts MongoDB only. API and workers are in the Compose profile `apps` so a later image build does not become the default path. Kubernetes is out of scope.
