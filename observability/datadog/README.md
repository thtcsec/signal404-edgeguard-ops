# Datadog plans

These notes are not dashboard JSON and are not imported anywhere.

## Sections

1. **Fleet Overview** — device count by status, active incidents, sites.
2. **Device Health** — CPU, memory, CPU temperature, GPU temperature, GPU usage. Filter by `device_id`, `site`, `line`.
3. **AI Inference Performance** — FPS, inference latency, dropped frames, current `profile`.
4. **Network Health** — packet loss and network latency, used to rule out a network cause.
5. **Active Incidents** — `edgeguard.incident.active` and recent incident logs.
6. **Incident Investigation** — one device, temperature against latency, with links to logs and traces.
7. **Remediation / Recovery** — profile changes, `edgeguard.remediation.count`, and the return to baseline.

Template files for import can be added under this directory after the trial account exists. Do not commit API keys inside them.
