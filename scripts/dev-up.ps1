$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose up -d mongodb
Write-Host "MongoDB is starting on localhost:27017. Application containers are behind the 'apps' profile and are not started."
