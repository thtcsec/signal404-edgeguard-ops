# MongoDB

Local development uses the `mongodb` service in the root `docker-compose.yml` (`mongo:8`, port 27017, database `edgeguard`). No users are created. No collections are created.

`scripts/dev-up.ps1` starts that container. `scripts/seed-placeholder.ps1` does not insert documents.

Collection names, the time-series options, TTL, and the planned `$setWindowFields` pipeline are in [docs/DATA_MODEL.md](../../docs/DATA_MODEL.md). Creating them is a build-window task. The MongoDB .NET driver is intentionally not referenced yet.
