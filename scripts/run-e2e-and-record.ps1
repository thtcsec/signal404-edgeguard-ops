# Automatic E2E (all workers already running) + terminal screen capture.
# Does not print secrets. Hides .env paths in window title only.
$ErrorActionPreference = "Stop"
$Repo = "D:\tu_projects\signal404-edgeguard-ops"
Set-Location $Repo
$Dotnet = "$env:USERPROFILE\.dotnet\dotnet.exe"
if (-not (Test-Path $Dotnet)) { $Dotnet = "dotnet" }

$RecDir = Join-Path $Repo "docs\video\recordings"
New-Item -ItemType Directory -Force -Path $RecDir, (Join-Path $Repo ".logs") | Out-Null
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$EvidenceOut = Join-Path $Repo "docs\evidence\e2e-app-demo-$RunId.json"

# Clear prior incident data for a clean demo run (collections only — never delete docs/evidence/*)
Write-Host "Clearing edgeguard collections for isolated demo run..."
docker exec edgeguard-ops-mongodb-1 mongosh --quiet --eval @"
db = db.getSiblingDB('edgeguard');
db.telemetry.drop();
db.incidents.drop();
db.remediation_actions.drop();
db.devices.drop();
print('cleared');
"@

# Observability env (no secrets printed)
$env:Observability__DatadogEnabled = "true"
$env:Observability__AgentHost = "127.0.0.1"
$env:Observability__LogDirectory = Join-Path $Repo ".logs"
$env:Observability__EnvironmentName = "development"
$env:DD_AGENT_HOST = "127.0.0.1"
$env:DD_ENV = "development"
$env:DD_TRACE_ENABLED = "true"
$env:DD_LOGS_INJECTION = "true"
# Clear UDS that breaks Windows APM
Remove-Item Env:DD_APM_RECEIVER_SOCKET -ErrorAction SilentlyContinue
Remove-Item Env:DD_DOGSTATSD_SOCKET -ErrorAction SilentlyContinue

Write-Host "Building Release..."
& $Dotnet build "$Repo\services\telemetry-api" -c Release -v q
& $Dotnet build "$Repo\services\health-analyzer" -c Release -v q
& $Dotnet build "$Repo\services\response-worker" -c Release -v q

function Start-EgService {
  param($Name, $Project, $DdService)
  $dir = Join-Path $Repo "services\$Project\bin\Release\net9.0"
  $log = Join-Path $RecDir "term-$Name-$RunId.log"
  $cmd = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
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
  $arg = "-NoExit -NoProfile -Command $cmd"
  Start-Process -FilePath "powershell.exe" -ArgumentList $arg -WindowStyle Normal
  Start-Sleep -Seconds 2
}

Write-Host "Starting API + analyzer + response-worker (automatic E2E)..."
Start-EgService -Name "api" -Project "telemetry-api" -DdService "edgeguard-telemetry-api"
Start-Sleep -Seconds 4
Start-EgService -Name "analyzer" -Project "health-analyzer" -DdService "edgeguard-health-analyzer"
Start-Sleep -Seconds 2
Start-EgService -Name "worker" -Project "response-worker" -DdService "edgeguard-response-worker"
Start-Sleep -Seconds 5

# Health check
try {
  $h = Invoke-WebRequest -Uri "http://127.0.0.1:5080/health" -UseBasicParsing -TimeoutSec 10
  Write-Host "API health:" $h.StatusCode
} catch {
  Write-Host "API health not ready yet:" $_.Exception.Message
}

# Desktop capture of primary monitor (1920x1080 crop if larger)
$DesktopCap = Join-Path $RecDir "desktop-e2e-$RunId.mp4"
$FfmpegJob = Start-Process -FilePath "ffmpeg" -ArgumentList @(
  "-y", "-f", "gdigrab", "-framerate", "30", "-offset_x", "0", "-offset_y", "0",
  "-video_size", "1920x1080", "-i", "desktop",
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", "-crf", "23",
  $DesktopCap
) -PassThru -WindowStyle Minimized

Write-Host "Desktop capture PID $($FfmpegJob.Id) -> $DesktopCap"

# Start simulator in new window
$SimLog = Join-Path $RecDir "term-sim-$RunId.log"
$simCmd = @"
Set-Location '$Repo\apps\device-simulator'
`$env:PYTHONPATH='src'
`$env:EDGEGUARD_TELEMETRY_URL='http://localhost:5080'
`$env:EDGEGUARD_DEVICE_COUNT='1'
`$env:EDGEGUARD_INTERVAL_SECONDS='1'
`$env:EDGEGUARD_SCENARIO='THERMAL_THROTTLE'
python -m edgeguard_simulator.main 2>&1 | Tee-Object -FilePath '$SimLog'
"@
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -NoProfile -Command $simCmd" -WindowStyle Normal

Write-Host "Waiting for RESOLVED (up to 4 minutes)..."
$deadline = (Get-Date).AddMinutes(4)
$final = $null
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 8
  $json = docker exec edgeguard-ops-mongodb-1 mongosh --quiet --eval @"
db = db.getSiblingDB('edgeguard');
const inc = db.incidents.find().sort({detectedAt:-1}).limit(1).toArray()[0];
const rem = db.remediation_actions.find().sort({requestedAt:-1}).limit(1).toArray()[0];
const dev = db.devices.findOne({deviceId:'edge-001'});
print(JSON.stringify({incident:inc, remediation:rem, device:dev}, null, 0));
"@
  try {
    $final = $json | ConvertFrom-Json
  } catch {
    Write-Host "poll parse skip"
    continue
  }
  $st = $final.incident.status
  Write-Host ("[{0}] incident={1} status={2} rem={3} commanded={4} reported={5}" -f `
    (Get-Date -Format "HH:mm:ss"), $final.incident.incidentId, $st, `
    $final.remediation.state, $final.device.commandedProfile, $final.device.reportedProfile)
  if ($st -eq "RESOLVED" -and $final.remediation.state -eq "VERIFIED") {
    Write-Host "E2E_COMPLETE"
    break
  }
}

# Extra 15s of recovery metrics on screen
Start-Sleep -Seconds 15

# Stop desktop capture
if ($FfmpegJob -and -not $FfmpegJob.HasExited) {
  Stop-Process -Id $FfmpegJob.Id -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 2
}

# Dump evidence JSON (no secrets)
$Evidence = @{
  run_id = $RunId
  mode = "automatic_e2e_workers_prestarted"
  captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  desktop_capture = (Resolve-Path $DesktopCap -ErrorAction SilentlyContinue).Path
  incident = $final.incident
  remediation = $final.remediation
  device = $final.device
}
$Evidence | ConvertTo-Json -Depth 8 | Set-Content -Path $EvidenceOut -Encoding UTF8
Write-Host "Evidence written:" $EvidenceOut
Write-Host "Desktop capture:" $DesktopCap

# Mongo snapshot terminal capture helper text file for editors
$MongoSnap = Join-Path $RecDir "mongo-snapshot-$RunId.txt"
docker exec edgeguard-ops-mongodb-1 mongosh --quiet --eval @"
db = db.getSiblingDB('edgeguard');
print('=== INCIDENT ===');
printjson(db.incidents.find().sort({detectedAt:-1}).limit(1).toArray()[0]);
print('=== REMEDIATION ===');
printjson(db.remediation_actions.find().sort({requestedAt:-1}).limit(1).toArray()[0]);
print('=== DEVICE ===');
printjson(db.devices.findOne({deviceId:'edge-001'}));
print('=== LAST 5 TELEMETRY ===');
printjson(db.telemetry.find().sort({timestamp:-1}).limit(5).toArray());
"@ | Set-Content -Path $MongoSnap -Encoding UTF8
Write-Host "Mongo snapshot:" $MongoSnap
Write-Host "DONE_E2E"
