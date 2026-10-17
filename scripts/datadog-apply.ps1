param(
    [string]$Site = $(if ($env:DD_SITE) { $env:DD_SITE } else { "datadoghq.com" }),
    [string]$ApiKey = $env:DD_API_KEY,
    [string]$AppKey = $env:DD_APP_KEY
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($ApiKey) -or [string]::IsNullOrWhiteSpace($AppKey)) {
    Write-Error "Set DD_API_KEY and DD_APP_KEY in the environment (or pass -ApiKey/-AppKey). Never commit keys."
}

$headers = @{
    "DD-API-KEY"         = $ApiKey
    "DD-APPLICATION-KEY" = $AppKey
    "Content-Type"       = "application/json"
}

$base = "https://api.$Site"

function Invoke-DdJson([string]$Method, [string]$Path, [string]$BodyPath) {
    $body = Get-Content -Raw -Path $BodyPath
    $uri = "$base$Path"
    Write-Host "$Method $uri"
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -Body $body
}

$dashboard = Invoke-DdJson -Method "POST" -Path "/api/v1/dashboard" -BodyPath (Join-Path $root "observability\datadog\dashboard-fleet-operations.json")
Write-Host "Dashboard id=$($dashboard.id) url=https://app.$Site/dashboard/$($dashboard.id)"

$monitor = Invoke-DdJson -Method "POST" -Path "/api/v1/monitor" -BodyPath (Join-Path $root "observability\datadog\monitor-thermal-gpu.json")
Write-Host "Monitor id=$($monitor.id) url=https://app.$Site/monitors/$($monitor.id)"

Write-Host "Applied EdgeGuard Datadog dashboard + thermal monitor from repository definitions."
