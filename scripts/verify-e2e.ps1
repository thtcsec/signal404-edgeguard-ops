<#
.SYNOPSIS
  Clean automatic E2E with workers already running. Asserts Mongo evidence correctly.

Device documents are keyed by MongoDB _id (not deviceId). Commanded profile is
stored on devices.profile; reported profile is telemetry.profile.

Exits 0 only if:
  - API /health is 200
  - incident.status = RESOLVED
  - remediation.state = VERIFIED
  - devices.findOne({_id:"edge-001"}).profile = safe
  - latest telemetry for edge-001 has profile=safe and is fresh (<30s)

Does not delete docs/evidence/* files. Drops live Mongo collections only.
#>
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Dotnet = if (Test-Path "$env:USERPROFILE\.dotnet\dotnet.exe") { "$env:USERPROFILE\.dotnet\dotnet.exe" } else { "dotnet" }

$RecDir = Join-Path $Repo "docs\video\recordings"
New-Item -ItemType Directory -Force -Path $RecDir, (Join-Path $Repo ".logs") | Out-Null
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$EvidenceOut = Join-Path $Repo "docs\evidence\e2e-verified-$RunId.json"
$ResultOut = Join-Path $Repo "docs\evidence\e2e-verified-$RunId.result.txt"
$MongoSnap = Join-Path $RecDir "mongo-snapshot-$RunId.txt"
$DesktopCap = Join-Path $RecDir "desktop-e2e-$RunId.mp4"
$FailReason = $null

function Write-Result([string]$Status, [string]$Detail) {
    $line = "$(Get-Date -Format o) $Status $Detail"
    Add-Content -Path $ResultOut -Value $line
    Write-Host $line
}

Write-Result "START" "run_id=$RunId automatic E2E (workers prestarted)"

# Stop leftover host services on 5080
Get-NetTCPConnection -LocalPort 5080 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-Process -Name "EdgeGuard.TelemetryApi","EdgeGuard.HealthAnalyzer","EdgeGuard.ResponseWorker","dotnet" -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like "*signal404-edgeguard-ops*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Starting MongoDB + Datadog Agent..."
docker compose up -d mongodb
docker compose --profile datadog up -d datadog-agent

$healthy = $false
for ($i = 0; $i -lt 24; $i++) {
    $ps = docker ps --format "{{.Names}}|{{.Status}}"
    if (($ps -match "mongodb-1.*healthy") -and ($ps -match "datadog-agent-1.*healthy")) {
        $healthy = $true
        break
    }
    Start-Sleep -Seconds 5
}
if (-not $healthy) {
    Write-Result "FAIL" "Docker services not healthy: $(docker ps --format '{{.Names}} {{.Status}}')"
    exit 2
}
Write-Result "OK" "MongoDB and Datadog Agent healthy"

Write-Host "Clearing live Mongo collections (not docs/evidence)..."
docker exec edgeguard-ops-mongodb-1 mongosh --quiet --eval @"
db = db.getSiblingDB('edgeguard');
db.telemetry.drop();
db.incidents.drop();
db.remediation_actions.drop();
db.devices.drop();
print('cleared');
"@

$env:Observability__DatadogEnabled = "true"
$env:Observability__AgentHost = "127.0.0.1"
$env:Observability__LogDirectory = Join-Path $Repo ".logs"
$env:Observability__EnvironmentName = "development"
$env:DD_AGENT_HOST = "127.0.0.1"
$env:DD_ENV = "development"
$env:DD_TRACE_ENABLED = "true"
$env:DD_LOGS_INJECTION = "true"
Remove-Item Env:DD_APM_RECEIVER_SOCKET -ErrorAction SilentlyContinue
Remove-Item Env:DD_DOGSTATSD_SOCKET -ErrorAction SilentlyContinue

Write-Host "Building Release services..."
& $Dotnet build "$Repo\services\telemetry-api" -c Release -v q
if ($LASTEXITCODE -ne 0) { Write-Result "FAIL" "telemetry-api build"; exit 2 }
& $Dotnet build "$Repo\services\health-analyzer" -c Release -v q
if ($LASTEXITCODE -ne 0) { Write-Result "FAIL" "health-analyzer build"; exit 2 }
& $Dotnet build "$Repo\services\response-worker" -c Release -v q
if ($LASTEXITCODE -ne 0) { Write-Result "FAIL" "response-worker build"; exit 2 }

function Start-EgService {
    param($Name, $Project, $DdService)
    $dir = Join-Path $Repo "services\$Project\bin\Release\net9.0"
    $log = Join-Path $RecDir "term-$Name-$RunId.log"
    $cmd = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
`$host.UI.RawUI.WindowTitle = 'EdgeGuard $Name'
`$env:Observability__DatadogEnabled='true'
`$env:Observability__AgentHost='127.0.0.1'
`$env:Observability__LogDirectory='$(Join-Path $Repo '.logs')'
`$env:Observability__EnvironmentName='development'
`$env:DD_AGENT_HOST='127.0.0.1'
`$env:DD_ENV='development'
`$env:DD_SERVICE='$DdService'
`$env:DD_TRACE_ENABLED='true'
`$env:DD_LOGS_INJECTION='true'
Remove-Item Env:DD_APM_RECEIVER_SOCKET -EA SilentlyContinue
. '$Repo\scripts\enable-datadog-dotnet-apm.ps1' -AppDirectory '$dir'
& '$Dotnet' run --project '$Repo\services\$Project' -c Release --no-build 2>&1 | Tee-Object -FilePath '$log'
"@
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit","-NoProfile","-Command", $cmd) -WindowStyle Normal | Out-Null
    Start-Sleep -Seconds 2
}

Write-Host "Starting API + analyzer + response-worker BEFORE thermal inject..."
Start-EgService -Name "api" -Project "telemetry-api" -DdService "edgeguard-telemetry-api"
Start-Sleep -Seconds 6
Start-EgService -Name "analyzer" -Project "health-analyzer" -DdService "edgeguard-health-analyzer"
Start-Sleep -Seconds 2
Start-EgService -Name "worker" -Project "response-worker" -DdService "edgeguard-response-worker"
Start-Sleep -Seconds 5

$healthOk = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $h = Invoke-WebRequest -Uri "http://127.0.0.1:5080/health" -UseBasicParsing -TimeoutSec 5
        if ($h.StatusCode -eq 200) { $healthOk = $true; break }
        Write-Result "WARN" "GET /health status=$($h.StatusCode)"
    } catch {
        Write-Host "health retry $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 2
}
if (-not $healthOk) {
    Write-Result "FAIL" "GET /health did not return 200"
    exit 2
}
Write-Result "OK" "GET /health 200"

# Desktop capture: self-limiting duration + fragmented MP4 so a hard stop still plays
$ffmpegArgs = @(
    "-y", "-f", "gdigrab", "-framerate", "30",
    "-offset_x", "0", "-offset_y", "0", "-video_size", "1920x1080",
    "-i", "desktop",
    "-t", "170",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22",
    "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
    $DesktopCap
)
$FfmpegJob = Start-Process -FilePath "ffmpeg" -ArgumentList $ffmpegArgs -PassThru -WindowStyle Minimized
Write-Host "Desktop capture PID $($FfmpegJob.Id) -> $DesktopCap"

$SimLog = Join-Path $RecDir "term-sim-$RunId.log"
$simCmd = @"
`$host.UI.RawUI.WindowTitle = 'EdgeGuard simulator THERMAL_THROTTLE'
Set-Location '$Repo\apps\device-simulator'
`$env:PYTHONPATH='src'
`$env:EDGEGUARD_TELEMETRY_URL='http://localhost:5080'
`$env:EDGEGUARD_DEVICE_COUNT='1'
`$env:EDGEGUARD_INTERVAL_SECONDS='1'
`$env:EDGEGUARD_SCENARIO='THERMAL_THROTTLE'
python -m edgeguard_simulator.main 2>&1 | Tee-Object -FilePath '$SimLog'
"@
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit","-NoProfile","-Command", $simCmd) -WindowStyle Normal | Out-Null
Write-Result "OK" "Simulator started (workers already running)"

$pollFile = Join-Path $Repo "scripts\mongo-poll-e2e.js"
$snapFile = Join-Path $Repo "scripts\mongo-snapshot-e2e.js"

function Invoke-MongoJs([string]$JsPath) {
    $name = Split-Path $JsPath -Leaf
    docker cp $JsPath "edgeguard-ops-mongodb-1:/tmp/$name" | Out-Null
    docker exec edgeguard-ops-mongodb-1 mongosh --quiet "/tmp/$name"
}

$final = $null
$deadline = (Get-Date).AddMinutes(4)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 6
    $raw = Invoke-MongoJs $pollFile
    try {
        $jsonLine = ($raw -split "`n" | Where-Object { $_.Trim().StartsWith("{") } | Select-Object -Last 1)
        $final = $jsonLine | ConvertFrom-Json
    } catch {
        Write-Host "poll parse skip: $raw"
        continue
    }
    $incId = $final.incident._id
    $st = $final.incident.status
    $rst = $final.remediation.state
    $dprof = $final.device.profile
    $tprof = $final.telemetry.profile
    Write-Host ("[{0}] incident={1} status={2} rem={3} device.profile={4} tel.profile={5} gpu={6}" -f `
        (Get-Date -Format "HH:mm:ss"), $incId, $st, $rst, $dprof, $tprof, $final.telemetry.gpuTemperature)
    if ($st -eq "RESOLVED" -and $rst -eq "VERIFIED") {
        Write-Host "LOOP_RESOLVED"
        break
    }
}

Start-Sleep -Seconds 8
$raw = Invoke-MongoJs $pollFile
$final = $raw | ConvertFrom-Json

# Snapshot (quotes preserved via file stdin)
Invoke-MongoJs $snapFile | Set-Content -Path $MongoSnap -Encoding UTF8

# Assertions
$assertions = @()
function Add-Assert([string]$Name, [bool]$Ok, [string]$Detail) {
    $script:assertions += @{ name = $Name; ok = $Ok; detail = $Detail }
    if ($Ok) { Write-Result "PASS" "$Name — $Detail" }
    else { Write-Result "FAIL" "$Name — $Detail"; $script:FailReason = $Name }
}

Add-Assert "incident_present" ($null -ne $final.incident._id) "id=$($final.incident._id)"
Add-Assert "incident_resolved" ($final.incident.status -eq "RESOLVED") "status=$($final.incident.status)"
Add-Assert "remediation_verified" ($final.remediation.state -eq "VERIFIED") "state=$($final.remediation.state)"
Add-Assert "device_found_by_id" ($null -ne $final.device._id) "_id=$($final.device._id)"
Add-Assert "device_profile_safe" ($final.device.profile -eq "safe") "profile=$($final.device.profile) status=$($final.device.status)"
Add-Assert "telemetry_profile_safe" ($final.telemetry.profile -eq "safe") "profile=$($final.telemetry.profile) status=$($final.telemetry.status)"

$telAge = $null
if ($final.telemetry.timestamp) {
    $ts = [datetime]$final.telemetry.timestamp
    $telAge = [math]::Round(((Get-Date).ToUniversalTime() - $ts.ToUniversalTime()).TotalSeconds, 1)
    Add-Assert "telemetry_fresh" ($telAge -lt 30) "age_s=$telAge gpu=$($final.telemetry.gpuTemperature) fps=$($final.telemetry.fps)"
} else {
    Add-Assert "telemetry_fresh" $false "no telemetry timestamp"
}

$scanLogs = @(
    (Join-Path $RecDir "term-api-$RunId.log"),
    (Join-Path $RecDir "term-analyzer-$RunId.log"),
    (Join-Path $RecDir "term-worker-$RunId.log")
)
$fatal = $false
foreach ($lf in $scanLogs) {
    if (Test-Path $lf) {
        $hits = Select-String -Path $lf -Pattern "Unhandled exception|fail:|Fatal|HTTP 500" -SimpleMatch:$false | Select-Object -First 5
        if ($hits) {
            Write-Result "WARN" "log hits in $(Split-Path $lf -Leaf): $($hits.Line)"
            if ($hits.Line -match "Unhandled exception|Fatal") { $fatal = $true }
        }
    }
}
Add-Assert "no_fatal_service_exceptions" (-not $fatal) "scanned api/analyzer/worker logs"

$passed = ($assertions | Where-Object { -not $_.ok }).Count -eq 0
$verdict = if ($passed) { "PASSED" } else { "FAILED" }

$evidence = @{
    run_id = $RunId
    verdict = $verdict
    mode = "automatic_e2e_workers_prestarted"
    captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    desktop_capture = $DesktopCap
    mongo_snapshot = $MongoSnap
    assertions = $assertions
    incident = $final.incident
    remediation = $final.remediation
    device = $final.device
    latest_telemetry = $final.telemetry
    note = "Device keyed by MongoDB _id. devices.profile is commanded safe profile. telemetry.profile is reported profile."
}
($evidence | ConvertTo-Json -Depth 10) | Set-Content -Path $EvidenceOut -Encoding utf8
Write-Result $verdict "evidence=$EvidenceOut"

# Let ffmpeg finish remaining seconds or stop after extra recovery footage
Start-Sleep -Seconds 12
if ($FfmpegJob -and -not $FfmpegJob.HasExited) {
    try {
        $FfmpegJob.StandardInput.WriteLine("q")
    } catch {
        Stop-Process -Id $FfmpegJob.Id -ErrorAction SilentlyContinue
    }
    Wait-Process -Id $FfmpegJob.Id -Timeout 8 -ErrorAction SilentlyContinue
}

if ($passed) {
    Write-Host "E2E_PASSED $RunId"
    exit 0
}
Write-Host "E2E_FAILED $FailReason"
exit 3
