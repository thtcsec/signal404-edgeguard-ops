# Datadog plans + applyable definitions

Repo-reproducible definitions. **Live apply** requires `DD_API_KEY` + `DD_APP_KEY` in local `.env` (loaded by `scripts/datadog-apply.ps1`). Never commit keys.

| File | Purpose |
| --- | --- |
| `dashboard-fleet-operations.json` | EdgeGuard Fleet Operations |
| `monitor-thermal-gpu.json` | Production-reasonable thermal monitor (`last_5m`, `new_group_delay` 60) |
| `monitor-thermal-gpu.demo.json` | Demo monitor (`last_2m`, `new_group_delay` 0) for ALERT before recovery |

```powershell
..\..\scripts\datadog-apply.ps1
..\..\scripts\datadog-apply.ps1 -Demo
```

Application is idempotent (update by dashboard title / monitor name). No webhook notification handles are included.
