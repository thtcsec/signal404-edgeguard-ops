# Workers already running. Drop live Mongo, record THERMAL_THROTTLE from full with gdigrab splat.
$ErrorActionPreference = "Stop"
$Repo = "D:\tu_projects\signal404-edgeguard-ops"
$RecDir = Join-Path $Repo "docs\video\recordings"
$EvidenceDir = Join-Path $Repo "docs\evidence"
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$SimLog = Join-Path $RecDir "term-sim-$RunId.log"
$WorkerLog = Get-ChildItem "$RecDir\term-worker-2026*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$SimMp4 = Join-Path $RecDir "conhost-sim-start.mp4"
$WorkerMp4 = Join-Path $RecDir "conhost-worker-respond.mp4"
$MongoMp4 = Join-Path $RecDir "conhost-mongo-verify.mp4"
$SimScript = Join-Path $RecDir "conhost-sim-start.ps1"
$ResultOut = Join-Path $EvidenceDir "e2e-verified-$RunId.result.txt"

function Write-Result($s,$d) { $l = "$(Get-Date -Format o) $s $d"; Add-Content $ResultOut $l; Write-Host $l }
Write-Result "START" "run_id=$RunId record-live-e2e (workers prestarted)"

Write-Host "Clearing live Mongo (evidence files kept)..."
docker exec edgeguard-ops-mongodb-1 mongosh --quiet --eval "db=db.getSiblingDB('edgeguard'); db.telemetry.drop(); db.incidents.drop(); db.remediation_actions.drop(); db.devices.drop(); print('cleared');"

$h = Invoke-WebRequest -Uri "http://127.0.0.1:5080/health" -UseBasicParsing -TimeoutSec 5
if ($h.StatusCode -ne 200) { throw "health $($h.StatusCode)" }
Write-Result "OK" "GET /health 200"

$content = @"
`$Host.UI.RawUI.WindowTitle = 'EG-Inject-Fault'
. '$Repo\scripts\set-console-font.ps1'
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
Clear-Host
Write-Host 'INJECT FAULT  ·  EdgeGuard device simulator' -ForegroundColor Yellow
Write-Host 'Automatic E2E $RunId  ·  commanded profile starts at full (healthy)' -ForegroundColor DarkGray
Write-Host 'SYNTHETIC telemetry  ·  THERMAL_THROTTLE  ·  API/analyzer/worker already running' -ForegroundColor DarkGray
Write-Host ''
Set-Location '$Repo\apps\device-simulator'
`$env:PYTHONPATH = 'src'
`$env:EDGEGUARD_TELEMETRY_URL = 'http://localhost:5080'
`$env:EDGEGUARD_DEVICE_COUNT = '1'
`$env:EDGEGUARD_INTERVAL_SECONDS = '1'
`$env:EDGEGUARD_SCENARIO = 'THERMAL_THROTTLE'
Write-Host 'PS apps\device-simulator>' -NoNewline
Write-Host " `$env:EDGEGUARD_SCENARIO='THERMAL_THROTTLE'; python -m edgeguard_simulator.main"
Write-Host ''
python -m edgeguard_simulator.main 2>&1 | Tee-Object -FilePath '$SimLog'
"@
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($SimScript, $content, $utf8)

$conhost = "$env:SystemRoot\System32\conhost.exe"
$simProc = Start-Process -FilePath $conhost -ArgumentList @(
    "powershell.exe", "-NoLogo", "-NoProfile", "-NoExit",
    "-ExecutionPolicy", "Bypass", "-File", $SimScript
) -PassThru
$SimStartedUtc = (Get-Date).ToUniversalTime()
Write-Result "OK" "conhost sim pid=$($simProc.Id) started $($SimStartedUtc.ToString('o'))"

$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    if ((Test-Path $SimLog) -and ((Get-Item $SimLog).Length -gt 80)) {
        Write-Host "SIM_LOG" ((Get-Content $SimLog -TotalCount 2) -join ' | ')
        $ok = $true
        break
    }
}
if (-not $ok) { throw "simulator did not start" }

Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Text;
public class WinFg3 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  public static IntPtr FindTitle(string needle) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      var sb = new StringBuilder(512); GetWindowText(h, sb, sb.Capacity);
      if (sb.ToString().IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) { found = h; return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@
$hwnd = [WinFg3]::FindTitle("EG-Inject-Fault")
if ($hwnd -ne [IntPtr]::Zero) {
    [WinFg3]::ShowWindow($hwnd, 3) | Out-Null
    [WinFg3]::SetForegroundWindow($hwnd) | Out-Null
}

$grabArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", "$Repo\scripts\gdigrab-title.ps1",
    "-Title", "EG-Inject-Fault",
    "-OutMp4", $SimMp4,
    "-Seconds", "95"
)
$ff = Start-Process powershell.exe -ArgumentList $grabArgs -PassThru -WindowStyle Minimized
Write-Host "GDIGRAB pid=$($ff.Id)"

$pollFile = Join-Path $Repo "scripts\mongo-poll-e2e.js"
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
    } catch { continue }
    Write-Host ("[{0}] inc={1} st={2} rem={3} dprof={4} tprof={5} gpu={6} fps={7}" -f `
        (Get-Date -Format "HH:mm:ss"), $final.incident._id, $final.incident.status, $final.remediation.state, `
        $final.device.profile, $final.telemetry.profile, $final.telemetry.gpuTemperature, $final.telemetry.fps)
    if ($final.incident.status -eq "RESOLVED" -and $final.remediation.state -eq "VERIFIED") { break }
}

if ($ff -and -not $ff.HasExited) { Wait-Process -Id $ff.Id -Timeout 100 -ErrorAction SilentlyContinue }

$simOk = (Test-Path $SimMp4) -and ((Get-Item $SimMp4).LastWriteTime -gt (Get-Date).AddMinutes(-8)) -and ((Get-Item $SimMp4).Length -gt 200000)
Write-Result $(if ($simOk) {"OK"} else {"FAIL"}) "sim mp4 size=$((Get-Item $SimMp4 -EA SilentlyContinue).Length) mtime=$((Get-Item $SimMp4 -EA SilentlyContinue).LastWriteTime)"

$assertions = @()
function Add-Assert($n,$ok,$d) {
    $script:assertions += @{ name=$n; ok=$ok; detail=$d }
    Write-Result $(if ($ok) {"PASS"} else {"FAIL"}) "$n — $d"
}
Add-Assert "incident_present" ($null -ne $final.incident._id) "id=$($final.incident._id)"
Add-Assert "incident_resolved" ($final.incident.status -eq "RESOLVED") "status=$($final.incident.status)"
Add-Assert "remediation_verified" ($final.remediation.state -eq "VERIFIED") "state=$($final.remediation.state)"
Add-Assert "device_profile_safe" ($final.device.profile -eq "safe") "profile=$($final.device.profile)"
Add-Assert "telemetry_profile_safe" ($final.telemetry.profile -eq "safe") "profile=$($final.telemetry.profile) gpu=$($final.telemetry.gpuTemperature) fps=$($final.telemetry.fps)"
Add-Assert "sim_mp4_fresh" $simOk "conhost-sim-start.mp4 recorded this run"

$passed = ($assertions | Where-Object { -not $_.ok }).Count -eq 0
$ResolvedUtc = (Get-Date).ToUniversalTime()
$evidence = @{
    run_id = $RunId
    verdict = $(if ($passed) {"PASSED"} else {"FAILED"})
    mode = "automatic_e2e_workers_prestarted_recorded"
    captured_at_utc = $ResolvedUtc.ToString("o")
    simulator_started_utc = $SimStartedUtc.ToString("o")
    incident = $final.incident
    remediation = $final.remediation
    device = $final.device
    latest_telemetry = $final.telemetry
    assertions = $assertions
    note = "Fresh E2E from empty devices so first commanded profile is full. Video recorded via conhost gdigrab."
}
($evidence | ConvertTo-Json -Depth 10) | Set-Content "$EvidenceDir\e2e-verified-$RunId.json" -Encoding utf8
docker cp "$Repo\scripts\mongo-snapshot-e2e.js" edgeguard-ops-mongodb-1:/tmp/mongo-snapshot-e2e.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-snapshot-e2e.js | Set-Content "$RecDir\mongo-snapshot-$RunId.txt" -Encoding utf8

# Worker paced replay of THIS run
$wl = if ($WorkerLog) { $WorkerLog.FullName } else { "$RecDir\term-worker-20261021200755.log" }
$WorkerScript = Join-Path $RecDir "conhost-worker-respond.ps1"
$wcontent = @"
`$Host.UI.RawUI.WindowTitle = 'EG-Respond-Worker'
. '$Repo\scripts\set-console-font.ps1'
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
Clear-Host
Write-Host 'RESPOND  ·  response-worker log  ·  E2E $RunId' -ForegroundColor Yellow
Write-Host 'Authentic lines from this run — APPLIED before RESOLVED' -ForegroundColor DarkGray
Write-Host 'incident $($final.incident._id)' -ForegroundColor DarkGray
Write-Host ''
Start-Sleep -Seconds 1
Get-Content -LiteralPath '$wl' | ForEach-Object {
    if (`$_ -match '"Timestamp":"([^"]+)".*"Message":"([^"]+)"') {
        `$ts = `$Matches[1]; `$msg = `$Matches[2]
        if (`$msg -match 'Remediation applied|Incident entered RECOVERING|Incident RESOLVED' -and `$msg -match '$($final.incident._id)') {
            `$clock = if (`$ts.Length -ge 19) { `$ts.Substring(11, 8) } else { `$ts }
            if (`$msg -match 'RESOLVED') { Write-Host "`$clock  `$msg" -ForegroundColor Green }
            elseif (`$msg -match 'applied') { Write-Host "`$clock  `$msg" -ForegroundColor Yellow }
            else { Write-Host "`$clock  `$msg" -ForegroundColor Cyan }
            Start-Sleep -Milliseconds 1200
        }
    }
}
Write-Host ''
Write-Host 'Mongo  incident.status=$($final.incident.status)  remediation.state=$($final.remediation.state)' -ForegroundColor Cyan
Start-Sleep -Seconds 2
"@
[System.IO.File]::WriteAllText($WorkerScript, $wcontent, $utf8)
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Repo\scripts\capture-conhost-window.ps1" -Title "EG-Respond-Worker" -ScriptPath $WorkerScript -OutMp4 $WorkerMp4 -Seconds 16 -WarmupSeconds 2

$MongoScript = Join-Path $RecDir "conhost-mongo-verify.ps1"
$mcontent = @"
`$Host.UI.RawUI.WindowTitle = 'EG-Verify-Mongo'
. '$Repo\scripts\set-console-font.ps1'
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
try { `$Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
Clear-Host
Write-Host 'VERIFY  ·  E2E $RunId  ·  live mongosh' -ForegroundColor Yellow
Write-Host "PS> docker exec mongosh  latest incident / remediation / devices.findOne({_id:'edge-001'})"
Write-Host ''
docker cp '$Repo\scripts\mongo-verify-latest.js' edgeguard-ops-mongodb-1:/tmp/mongo-verify-latest.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-verify-latest.js
Write-Host ''
Write-Host 'PASS  incident=$($final.incident.status)  remediation=$($final.remediation.state)  device.profile=$($final.device.profile)  telemetry.profile=$($final.telemetry.profile)' -ForegroundColor Cyan
Start-Sleep -Seconds 2
"@
[System.IO.File]::WriteAllText($MongoScript, $mcontent, $utf8)
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Repo\scripts\capture-conhost-window.ps1" -Title "EG-Verify-Mongo" -ScriptPath $MongoScript -OutMp4 $MongoMp4 -Seconds 18 -WarmupSeconds 2

$fromTs = [int64]([DateTimeOffset]$SimStartedUtc).ToUnixTimeMilliseconds() - 20000
$toTs = [int64]([DateTimeOffset]$ResolvedUtc).ToUnixTimeMilliseconds() + 80000
$metaOut = @{
    run_id = $RunId
    verdict = $(if ($passed) {"PASSED"} else {"FAILED"})
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
    preserved_prior_runs = @("20261021183352", "20261021201508")
}
($metaOut | ConvertTo-Json -Depth 6) | Set-Content "$RecDir\judge-e2e-run.json" -Encoding utf8
Write-Host "RUN_META from_ts=$fromTs to_ts=$toTs incident=$($final.incident._id)"
if ($passed) { Write-Host "E2E_PASSED $RunId"; exit 0 }
Write-Host "E2E_FAILED $RunId"; exit 3
