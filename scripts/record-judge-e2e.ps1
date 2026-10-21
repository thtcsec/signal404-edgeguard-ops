<#
.SYNOPSIS
  New automatic E2E from a healthy full profile, with authentic conhost recordings.

Preserves docs/evidence/* from prior runs. Drops live Mongo collections only after
a mongodump backup. Starts API / analyzer / worker, then records the simulator
starting THERMAL_THROTTLE from commanded profile=full.

Does not rewrite backend services.
#>
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Dotnet = if (Test-Path "$env:USERPROFILE\.dotnet\dotnet.exe") { "$env:USERPROFILE\.dotnet\dotnet.exe" } else { "dotnet" }

$RecDir = Join-Path $Repo "docs\video\recordings"
$EvidenceDir = Join-Path $Repo "docs\evidence"
New-Item -ItemType Directory -Force -Path $RecDir, $EvidenceDir, (Join-Path $Repo ".logs") | Out-Null
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$EvidenceOut = Join-Path $EvidenceDir "e2e-verified-$RunId.json"
$ResultOut = Join-Path $EvidenceDir "e2e-verified-$RunId.result.txt"
$MongoSnap = Join-Path $RecDir "mongo-snapshot-$RunId.txt"
$SimMp4 = Join-Path $RecDir "conhost-sim-start.mp4"
$WorkerMp4 = Join-Path $RecDir "conhost-worker-respond.mp4"
$MongoMp4 = Join-Path $RecDir "conhost-mongo-verify.mp4"
$RunMeta = Join-Path $RecDir "judge-e2e-run.json"
$FailReason = $null
$SimStartedUtc = $null

function Write-Result([string]$Status, [string]$Detail) {
    $line = "$(Get-Date -Format o) $Status $Detail"
    Add-Content -Path $ResultOut -Value $line
    Write-Host $line
}

function Backup-CurrentVideo {
    $final = Join-Path $Repo "docs\video\edgeguard-ops-final-demo.mp4"
    if (Test-Path $final) {
        $bak = Join-Path $Repo "docs\video\edgeguard-ops-final-demo.pre-editorial-rebuild.mp4"
        Copy-Item -Force $final $bak
        Write-Result "OK" "backed up current mp4 -> $bak"
    }
}

function Backup-Mongo {
    $bakHost = Join-Path $EvidenceDir "mongo-backup-pre-editorial"
    New-Item -ItemType Directory -Force -Path $bakHost | Out-Null
    docker exec edgeguard-ops-mongodb-1 mongodump --db=edgeguard --out=/tmp/eg-backup | Out-Null
    docker cp edgeguard-ops-mongodb-1:/tmp/eg-backup/edgeguard $bakHost
    Write-Result "OK" "mongodump -> $bakHost"
}

Write-Result "START" "run_id=$RunId judge E2E (workers first, then thermal from full)"

Backup-CurrentVideo

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
    Write-Result "FAIL" "Docker services not healthy"
    exit 2
}
Write-Result "OK" "MongoDB and Datadog Agent healthy"

Backup-Mongo

Get-NetTCPConnection -LocalPort 5080 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-Process -Name "EdgeGuard.TelemetryApi","EdgeGuard.HealthAnalyzer","EdgeGuard.ResponseWorker","dotnet" -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like "*signal404-edgeguard-ops*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "edgeguard_simulator" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Clearing live Mongo collections (evidence files kept)..."
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
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit","-NoProfile","-Command", $cmd) -WindowStyle Minimized | Out-Null
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
    } catch {
        Write-Host "health retry $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 2
}
if (-not $healthOk) {
    Write-Result "FAIL" "GET /health did not return 200"
    exit 2
}
Write-Result "OK" "GET /health 200 — workers running, device collection empty (full profile on first ingest)"

$SimLog = Join-Path $RecDir "term-sim-$RunId.log"
$SimScript = Join-Path $RecDir "conhost-sim-start.ps1"
@"
`$Host.UI.RawUI.WindowTitle = "EG Inject Fault"
. "$Repo\scripts\set-console-font.ps1"
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
Clear-Host
Write-Host "INJECT FAULT  ·  EdgeGuard device simulator" -ForegroundColor Yellow
Write-Host "Fresh automatic E2E $RunId  ·  start commanded profile=full (healthy)" -ForegroundColor DarkGray
Write-Host "SYNTHETIC telemetry  ·  scenario=THERMAL_THROTTLE  ·  workers already running" -ForegroundColor DarkGray
Write-Host ""
Set-Location "$Repo\apps\device-simulator"
`$env:PYTHONPATH = "src"
`$env:EDGEGUARD_TELEMETRY_URL = "http://localhost:5080"
`$env:EDGEGUARD_DEVICE_COUNT = "1"
`$env:EDGEGUARD_INTERVAL_SECONDS = "1"
`$env:EDGEGUARD_SCENARIO = "THERMAL_THROTTLE"
Write-Host "PS apps\device-simulator>" -NoNewline
Write-Host " `$env:EDGEGUARD_SCENARIO='THERMAL_THROTTLE'; python -m edgeguard_simulator.main" -ForegroundColor White
Write-Host ""
python -m edgeguard_simulator.main 2>&1 | Tee-Object -FilePath "$SimLog"
"@ | Set-Content -Path $SimScript -Encoding UTF8

$SimStartedUtc = (Get-Date).ToUniversalTime()
Write-Result "OK" "Starting recorded simulator (conhost GDI) at $($SimStartedUtc.ToString('o'))"
$capArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Repo "scripts\capture-conhost-window.ps1"),
    "-Title", "EG Inject Fault",
    "-ScriptPath", $SimScript,
    "-OutMp4", $SimMp4,
    "-Seconds", "105",
    "-WarmupSeconds", "3",
    "-KeepAlive"
)
$CapProc = Start-Process -FilePath "powershell.exe" -ArgumentList $capArgs -PassThru -WindowStyle Minimized
Write-Host "SIM_CAPTURE pid=$($CapProc.Id)"

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
    Start-Sleep -Seconds 5
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
    Write-Host ("[{0}] incident={1} status={2} rem={3} device.profile={4} tel.profile={5} gpu={6} fps={7}" -f `
        (Get-Date -Format "HH:mm:ss"), $incId, $st, $rst, $dprof, $tprof, $final.telemetry.gpuTemperature, $final.telemetry.fps)
    if ($st -eq "RESOLVED" -and $rst -eq "VERIFIED") {
        Write-Host "LOOP_RESOLVED"
        break
    }
}

Start-Sleep -Seconds 4
$raw = Invoke-MongoJs $pollFile
$final = ($raw -split "`n" | Where-Object { $_.Trim().StartsWith("{") } | Select-Object -Last 1) | ConvertFrom-Json
Invoke-MongoJs $snapFile | Set-Content -Path $MongoSnap -Encoding UTF8

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

$workerLog = Join-Path $RecDir "term-worker-$RunId.log"
$appliedHit = $false
$resolvedHit = $false
if (Test-Path $workerLog) {
    $appliedHit = [bool](Select-String -LiteralPath $workerLog -Pattern "Remediation applied" -SimpleMatch | Select-Object -First 1)
    $resolvedHit = [bool](Select-String -LiteralPath $workerLog -Pattern "Incident RESOLVED" -SimpleMatch | Select-Object -First 1)
}
Add-Assert "worker_applied_logged" $appliedHit "Remediation applied in $workerLog"
Add-Assert "worker_resolved_logged" $resolvedHit "Incident RESOLVED in $workerLog"

$passed = ($assertions | Where-Object { -not $_.ok }).Count -eq 0
$verdict = if ($passed) { "PASSED" } else { "FAILED" }
$ResolvedUtc = (Get-Date).ToUniversalTime()

$evidence = @{
    run_id = $RunId
    verdict = $verdict
    mode = "automatic_e2e_workers_prestarted_judge_rebuild"
    captured_at_utc = $ResolvedUtc.ToString("o")
    simulator_started_utc = $SimStartedUtc.ToString("o")
    mongo_snapshot = $MongoSnap
    simulator_mp4 = $SimMp4
    assertions = $assertions
    incident = $final.incident
    remediation = $final.remediation
    device = $final.device
    latest_telemetry = $final.telemetry
    note = "Fresh E2E from empty devices collection so first commanded profile is full. Device keyed by Mongo _id."
}
($evidence | ConvertTo-Json -Depth 10) | Set-Content -Path $EvidenceOut -Encoding utf8
Write-Result $verdict "evidence=$EvidenceOut"

if ($CapProc -and -not $CapProc.HasExited) {
    Write-Host "Waiting for simulator capture to finish..."
    Wait-Process -Id $CapProc.Id -Timeout 120 -ErrorAction SilentlyContinue
}

$WorkerScript = Join-Path $RecDir "conhost-worker-respond.ps1"
@"
`$Host.UI.RawUI.WindowTitle = "EG Respond Worker"
. "$Repo\scripts\set-console-font.ps1"
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
Clear-Host
Write-Host "RESPOND  ·  response-worker  ·  E2E $RunId" -ForegroundColor Yellow
Write-Host "Authentic log lines from this run — APPLIED before RESOLVED" -ForegroundColor DarkGray
Write-Host "incident $($final.incident._id)" -ForegroundColor DarkGray
Write-Host ""
Start-Sleep -Seconds 1
Get-Content -LiteralPath "$workerLog" | ForEach-Object {
    if (`$_ -match '"Timestamp":"([^"]+)".*"Message":"([^"]+)"') {
        `$ts = `$Matches[1]
        `$msg = `$Matches[2]
        if (`$msg -match 'Remediation applied|Incident entered RECOVERING|Incident RESOLVED|Opened thermal') {
            `$clock = if (`$ts.Length -ge 19) { `$ts.Substring(11, 8) } else { `$ts }
            if (`$msg -match 'RESOLVED') { Write-Host "`$clock  `$msg" -ForegroundColor Green }
            elseif (`$msg -match 'applied') { Write-Host "`$clock  `$msg" -ForegroundColor Yellow }
            else { Write-Host "`$clock  `$msg" -ForegroundColor Cyan }
            Start-Sleep -Milliseconds 1100
        }
    }
}
Write-Host ""
Write-Host "Mongo  incident.status=$($final.incident.status)  remediation.state=$($final.remediation.state)" -ForegroundColor Cyan
Start-Sleep -Seconds 2
"@ | Set-Content -Path $WorkerScript -Encoding UTF8

Write-Host "Recording worker APPLIED -> RESOLVED console..."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Repo "scripts\capture-conhost-window.ps1") `
    -Title "EG Respond Worker" -ScriptPath $WorkerScript -OutMp4 $WorkerMp4 -Seconds 16 -WarmupSeconds 2

$MongoScript = Join-Path $RecDir "conhost-mongo-verify.ps1"
@"
`$Host.UI.RawUI.WindowTitle = "EG Verify Mongo"
. "$Repo\scripts\set-console-font.ps1"
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
Clear-Host
Write-Host "VERIFY  ·  E2E $RunId  ·  live mongosh" -ForegroundColor Yellow
Write-Host "PS> docker exec mongosh  latest incident / remediation / devices.findOne({_id:'edge-001'})" -ForegroundColor White
Write-Host ""
docker cp "$Repo\scripts\mongo-verify-latest.js" edgeguard-ops-mongodb-1:/tmp/mongo-verify-latest.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-verify-latest.js
Write-Host ""
Write-Host "PASS  incident=$($final.incident.status)  remediation=$($final.remediation.state)  device.profile=$($final.device.profile)  telemetry.profile=$($final.telemetry.profile)" -ForegroundColor Cyan
Start-Sleep -Seconds 2
"@ | Set-Content -Path $MongoScript -Encoding UTF8

Write-Host "Recording mongosh verify..."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Repo "scripts\capture-conhost-window.ps1") `
    -Title "EG Verify Mongo" -ScriptPath $MongoScript -OutMp4 $MongoMp4 -Seconds 18 -WarmupSeconds 2

$fromTs = [int64]([DateTimeOffset]$SimStartedUtc).ToUnixTimeMilliseconds() - 30000
$toTs = [int64]([DateTimeOffset]$ResolvedUtc).ToUnixTimeMilliseconds() + 90000
$metaOut = @{
    run_id = $RunId
    verdict = $verdict
    incident_id = $final.incident._id
    remediation_id = $final.remediation._id
    detected_at = $final.incident.detectedAt
    resolved_at = $final.incident.resolvedAt
    simulator_started_utc = $SimStartedUtc.ToString("o")
    captured_at_utc = $ResolvedUtc.ToString("o")
    from_ts = $fromTs
    to_ts = $toTs
    simulator_mp4 = "docs/video/recordings/conhost-sim-start.mp4"
    worker_mp4 = "docs/video/recordings/conhost-worker-respond.mp4"
    mongo_mp4 = "docs/video/recordings/conhost-mongo-verify.mp4"
    evidence = "docs/evidence/e2e-verified-$RunId.json"
}
($metaOut | ConvertTo-Json -Depth 6) | Set-Content -Path $RunMeta -Encoding utf8
Write-Host "RUN_META $RunMeta from_ts=$fromTs to_ts=$toTs"

if ($passed) {
    Write-Host "E2E_PASSED $RunId"
    exit 0
}
Write-Host "E2E_FAILED $FailReason"
exit 3
