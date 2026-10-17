# telemetry-api

ASP.NET Core 9 minimal API.

- `GET /health` — process + MongoDB ping
- `POST /telemetry` — validate payload, insert into MongoDB time-series, upsert device

```powershell
& "$env:USERPROFILE\.dotnet\dotnet.exe" run --project .
```

Listens on `http://localhost:5080` in Development (`Properties/launchSettings.json`).
