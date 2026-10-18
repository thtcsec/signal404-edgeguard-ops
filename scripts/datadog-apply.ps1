<#
.SYNOPSIS
  Idempotently create/update the EdgeGuard Fleet Operations dashboard and thermal monitor.

.PARAMETER Demo
  Apply the demo thermal monitor (last_2m, new_group_delay 0) instead of the production definition.

.PARAMETER EnvFile
  Path to a local .env file (default: repo-root .env). Loaded into the process if present.
#>
param(
    [string]$Site = "",
    [string]$ApiKey = "",
    [string]$AppKey = "",
    [string]$EnvFile = "",
    [switch]$Demo
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Import-DotEnv([string]$Path) {
    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $idx = $line.IndexOf("=")
        if ($idx -lt 1) {
            return
        }

        $name = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        # Do not overwrite explicitly provided process env / parameters.
        if (-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
            return
        }

        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }

    Write-Host "Loaded environment from $Path"
}

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
    $EnvFile = Join-Path $root ".env"
}

Import-DotEnv -Path $EnvFile

if ([string]::IsNullOrWhiteSpace($Site)) {
    $Site = if ($env:DD_SITE) { $env:DD_SITE } else { "datadoghq.com" }
}
if ([string]::IsNullOrWhiteSpace($ApiKey)) { $ApiKey = $env:DD_API_KEY }
if ([string]::IsNullOrWhiteSpace($AppKey)) { $AppKey = $env:DD_APP_KEY }

if ([string]::IsNullOrWhiteSpace($ApiKey) -or [string]::IsNullOrWhiteSpace($AppKey)) {
    Write-Error "Set DD_API_KEY and DD_APP_KEY in .env (or pass -ApiKey/-AppKey). Never commit keys."
}

$headers = @{
    "DD-API-KEY"         = $ApiKey
    "DD-APPLICATION-KEY" = $AppKey
    "Content-Type"       = "application/json"
}

$base = "https://api.$Site"

function Invoke-Dd {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [AllowNull()][string]$Body
    )

    Write-Host "$Method $Uri"
    # [string]$Body = $null becomes "" in PowerShell; never send -Body on GET/DELETE.
    if ([string]::IsNullOrEmpty($Body)) {
        $getHeaders = @{
            "DD-API-KEY"         = $headers["DD-API-KEY"]
            "DD-APPLICATION-KEY" = $headers["DD-APPLICATION-KEY"]
        }
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $getHeaders
    }

    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $headers -Body $Body
}

function Get-DashboardIdByTitle([string]$Title) {
    $resp = Invoke-Dd -Method "GET" -Uri "$base/api/v1/dashboard"
    $match = @($resp.dashboards) | Where-Object { $_.title -eq $Title } | Select-Object -First 1
    if ($match) { return [string]$match.id }
    return $null
}

function Get-MonitorIdByName([string]$Name) {
    $encoded = [uri]::EscapeDataString($Name)
    $resp = Invoke-Dd -Method "GET" -Uri "$base/api/v1/monitor?name=$encoded"
    $exact = @($resp) | Where-Object { $_.name -eq $Name } | Select-Object -First 1
    if ($exact) { return [int]$exact.id }
    return $null
}

$dashboardPath = Join-Path $root "observability\datadog\dashboard-fleet-operations.json"
$dashboardBody = Get-Content -Raw -Path $dashboardPath
$dashboardTitle = (Get-Content -Raw -Path $dashboardPath | ConvertFrom-Json).title
$existingDashboardId = Get-DashboardIdByTitle -Title $dashboardTitle

if ($existingDashboardId) {
    $dashboard = Invoke-Dd -Method "PUT" -Uri "$base/api/v1/dashboard/$existingDashboardId" -Body $dashboardBody
    Write-Host "Updated dashboard id=$existingDashboardId url=https://app.$Site/dashboard/$existingDashboardId"
} else {
    $dashboard = Invoke-Dd -Method "POST" -Uri "$base/api/v1/dashboard" -Body $dashboardBody
    Write-Host "Created dashboard id=$($dashboard.id) url=https://app.$Site/dashboard/$($dashboard.id)"
}

$monitorFile = if ($Demo) { "monitor-thermal-gpu.demo.json" } else { "monitor-thermal-gpu.json" }
$monitorPath = Join-Path $root "observability\datadog\$monitorFile"
$monitorBody = Get-Content -Raw -Path $monitorPath
$monitorName = (Get-Content -Raw -Path $monitorPath | ConvertFrom-Json).name
$existingMonitorId = Get-MonitorIdByName -Name $monitorName

if ($existingMonitorId) {
    $monitor = Invoke-Dd -Method "PUT" -Uri "$base/api/v1/monitor/$existingMonitorId" -Body $monitorBody
    Write-Host "Updated monitor id=$existingMonitorId ($monitorName) url=https://app.$Site/monitors/$existingMonitorId"
} else {
    $monitor = Invoke-Dd -Method "POST" -Uri "$base/api/v1/monitor" -Body $monitorBody
    Write-Host "Created monitor id=$($monitor.id) ($monitorName) url=https://app.$Site/monitors/$($monitor.id)"
}

Write-Host "Applied EdgeGuard Datadog definitions from repository (idempotent)."
