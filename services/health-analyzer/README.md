# health-analyzer

.NET worker that evaluates fleet telemetry with a MongoDB aggregation pipeline (`$setWindowFields`) and opens thermal incidents.

Detection signal:

- GPU 1-minute average hot (absolute or vs 5-minute baseline)
- inference latency / FPS degraded
- packet loss still low (rules out network)

```powershell
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project .
```
