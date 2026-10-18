<#
.SYNOPSIS
  Sets CORECLR profiler env vars so Datadog.Trace.Bundle automatic instrumentation loads.

.DESCRIPTION
  Call once per shell before `dotnet run` / starting a published DLL.
  Points at the `datadog/` folder copied next to the service output by Datadog.Trace.Bundle.

  On Windows host + Docker Agent, Unix domain sockets from Datadog's docker-run wizard
  (DD_APM_RECEIVER_SOCKET=/var/run/datadog/apm.socket) break tracing. This script clears
  those and forces TCP to 127.0.0.1:8126.

.PARAMETER AppDirectory
  Directory containing the app DLL and the `datadog` tracer home (build output or publish folder).

.EXAMPLE
  . .\scripts\enable-datadog-dotnet-apm.ps1 -AppDirectory .\services\telemetry-api\bin\Debug\net9.0
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$AppDirectory
)

$ErrorActionPreference = "Stop"
$appDir = (Resolve-Path $AppDirectory).Path
$tracerHome = Join-Path $appDir "datadog"
$profiler = Join-Path $tracerHome "win-x64\Datadog.Trace.ClrProfiler.Native.dll"

if (-not (Test-Path $profiler)) {
    Write-Error "Datadog profiler not found at '$profiler'. Build the service after referencing Datadog.Trace.Bundle."
}

$env:CORECLR_ENABLE_PROFILING = "1"
$env:CORECLR_PROFILER = "{846F5F1C-F9AE-4B07-969E-05C26BC060D8}"
$env:CORECLR_PROFILER_PATH = $profiler
$env:DD_DOTNET_TRACER_HOME = $tracerHome
$env:DD_TRACE_ENABLED = "true"
$env:DD_TRACE_OTEL_ENABLED = "true"
$env:DD_LOGS_INJECTION = "true"

# Host .NET → Docker Agent must use TCP, not Linux UDS paths from wizard .env paste-ins.
Remove-Item Env:\DD_APM_RECEIVER_SOCKET -ErrorAction SilentlyContinue
Remove-Item Env:\DD_DOGSTATSD_SOCKET -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("DD_APM_RECEIVER_SOCKET", $null, "Process")
[Environment]::SetEnvironmentVariable("DD_DOGSTATSD_SOCKET", $null, "Process")

if (-not $env:DD_AGENT_HOST) { $env:DD_AGENT_HOST = "127.0.0.1" }
if (-not $env:DD_TRACE_AGENT_PORT) { $env:DD_TRACE_AGENT_PORT = "8126" }
$env:DD_TRACE_AGENT_URL = "http://$($env:DD_AGENT_HOST):$($env:DD_TRACE_AGENT_PORT)"
if (-not $env:DD_ENV) { $env:DD_ENV = "development" }

Write-Host "Datadog .NET APM enabled for AppDirectory=$appDir"
Write-Host "  DD_DOTNET_TRACER_HOME=$tracerHome"
Write-Host "  CORECLR_PROFILER_PATH=$profiler"
Write-Host "  DD_TRACE_AGENT_URL=$($env:DD_TRACE_AGENT_URL) (TCP; UDS sockets cleared)"
