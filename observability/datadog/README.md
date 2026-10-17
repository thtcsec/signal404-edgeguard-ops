# Datadog plans + applyable definitions

Repo-reproducible definitions (implemented). **Live apply not yet verified** — requires `DD_API_KEY` + `DD_APP_KEY` in local env; never commit keys.

- `dashboard-fleet-operations.json` — EdgeGuard Fleet Operations dashboard
- `monitor-thermal-gpu.json` — GPU thermal ALERT → OK monitor
- Apply with `..\..\scripts\datadog-apply.ps1`

## Dashboard sections (definition intent)

1. **Fleet Overview** — active incidents and remediation signals
2. **Device Health** — GPU temperature and related device gauges
3. **AI Inference Performance** — FPS, inference latency
4. **Network Health** — packet loss
5. **Active Incidents** — `edgeguard.incident.active`
6. **Remediation / Recovery** — `edgeguard.remediation.count` on the same timeline

After a trial account exists, apply these files and confirm widgets/monitor state in the Datadog UI.
