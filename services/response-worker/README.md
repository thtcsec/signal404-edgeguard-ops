# response-worker

Polls MongoDB for active incidents, switches the device to `safe`, waits for recovery telemetry, then marks the incident `RESOLVED`.

Change streams are intentionally not used: local Compose runs standalone MongoDB without a replica set.

```powershell
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project .
```
