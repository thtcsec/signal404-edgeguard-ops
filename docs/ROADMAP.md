# Roadmap

Solo build. One convincing incident, not more services.

## Done before 2026-10-17

Scaffold recorded in [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md).

## Official build window: 2026-10-17 → 2026-10-31

Submission deadline: **2026-10-31 23:59 ICT**.

### Done

1. Create the `telemetry` time-series collection (`expireAfterSeconds`) and regular collections.
2. Implement ingest on `POST /telemetry` and synthetic simulator (`NORMAL`, `THERMAL_THROTTLE`, …).
3. Health analyzer: aggregation + `$setWindowFields`, open thermal incident.
4. Response worker: poll incidents, switch to safe profile, observe recovery, resolve.
5. Simulator honors commanded device profile (does not overwrite remediations).

### Next

6. Datadog: metrics/logs/traces, dashboard, thermal monitor.
7. Demo video, slides, submission disclosure.

## Explicitly deferred

Kubernetes, Kafka, Redis, RabbitMQ, custom frontend, authentication, multi-cloud, ML models, LLM agents.
