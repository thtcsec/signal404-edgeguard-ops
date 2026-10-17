$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose up -d mongodb
Write-Host "MongoDB is starting on localhost:27017."
Write-Host "Datadog agent is behind profile 'datadog' (not started)."
Write-Host "  docker compose --profile datadog up -d datadog-agent"
Write-Host "Application containers are behind profile 'apps'."
