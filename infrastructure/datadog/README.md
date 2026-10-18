# Datadog (local)

## Safe defaults

- Agent is behind Compose profile `datadog` — `.\scripts\dev-up.ps1` does **not** start it.
- `DD_API_KEY` must come from local `.env` (see `.env.example`). Never commit secrets.
- Application services keep `Observability__DatadogEnabled=false` unless you opt in.

## Start agent

```powershell
Copy-Item .env.example .env   # then set DD_API_KEY (and DD_APP_KEY for apply)
New-Item -ItemType Directory -Force -Path .logs | Out-Null
docker compose --profile datadog up -d datadog-agent
```

Host processes should point at:

- DogStatsD: `127.0.0.1:8125`
- Trace agent: `127.0.0.1:8126`
- Logs: absolute `Observability__LogDirectory` → repo `.logs` (mounted at `/var/log/edgeguard`)

APM on Windows host:

```powershell
. .\scripts\enable-datadog-dotnet-apm.ps1 -AppDirectory .\services\telemetry-api\bin\Release\net9.0
```

## Apply dashboard + monitor from repo

```powershell
.\scripts\datadog-apply.ps1           # loads .env; idempotent
.\scripts\datadog-apply.ps1 -Demo     # shorter window for hackathon ALERT→OK
```

Requires `DD_API_KEY` and `DD_APP_KEY` in `.env` or parameters. `DD_SITE` defaults to `datadoghq.com`.
