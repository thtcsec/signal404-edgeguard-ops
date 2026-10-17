# MongoDB

Local development uses the `mongodb` service in the root `docker-compose.yml` (`mongo:8`, port 27017, database `edgeguard`).

`scripts/dev-up.ps1` starts that container.

On first API start, `EdgeGuardMongoContext` creates:

- `telemetry` — time-series (`timestamp`, `metadata`, granularity seconds, `expireAfterSeconds` from config, default 14 days)
- `devices`, `incidents`, `remediation_actions` — regular collections + indexes

The MongoDB .NET driver is referenced from `EdgeGuard.Shared`. See [docs/DATA_MODEL.md](../../docs/DATA_MODEL.md).
