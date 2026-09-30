$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose --profile apps down
Write-Host "Compose project stopped."
