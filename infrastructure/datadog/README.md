# Datadog (local)

## Safe defaults

- Agent is behind Compose profile `datadog` — `.\scripts\dev-up.ps1` does **not** start it.
- `DD_API_KEY` must come from `.env` (see `.env.example`). Never commit secrets.
- Application services keep `Observability__DatadogEnabled=false` unless you opt in.

## Start agent

```powershell
Copy-Item .env.example .env   # then set DD_API_KEY
docker compose --profile datadog up -d datadog-agent
```

Host processes should point at:

- DogStatsD: `127.0.0.1:8125`
- Trace agent: `127.0.0.1:8126`

```powershell
$env:Observability__DatadogEnabled = "true"
$env:Observability__AgentHost = "127.0.0.1"
$env:DD_TRACE_ENABLED = "true"
$env:DD_TRACE_OTEL_ENABLED = "true"
$env:DD_AGENT_HOST = "127.0.0.1"
$env:DD_SERVICE = "edgeguard-telemetry-api"
$env:DD_ENV = "development"
```

## Apply dashboard + monitor from repo

```powershell
.\scripts\datadog-apply.ps1
```

Requires `DD_API_KEY` and optional `DD_SITE` (default `datadoghq.com`).
