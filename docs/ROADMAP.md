# Roadmap

Solo build. The goal is one convincing incident, not more services.

## Done before 2026-10-10

Scaffold recorded in [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md).

## Build window, 2026-10-10 to 2026-10-24

1. Create the `telemetry` time-series collection and the three regular collections.
2. Implement ingest on `POST /telemetry` and a synthetic simulator, including `THERMAL_THROTTLE`.
3. Implement the window aggregation and open one incident from it.
4. Emit metrics, logs, and traces to Datadog. Build the dashboard and the thermal monitor.
5. Implement safe-profile remediation and show the same monitor return to OK.
6. Record the demo and write the submission, including the reuse disclosure.

## Explicitly deferred

Kubernetes, Kafka, Redis, RabbitMQ, a custom frontend, authentication, multi-cloud, models, and LLM agents. Add one of these only if the demo is blocked without it. Redis and a message broker are not expected to be necessary.
