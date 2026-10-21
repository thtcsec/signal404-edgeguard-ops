# Record a dedicated mongosh + worker-log window by title (not the whole personal desktop).
$ErrorActionPreference = "Stop"
$Repo = "D:\tu_projects\signal404-edgeguard-ops"
$Rec = Join-Path $Repo "docs\video\recordings"
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$Out = Join-Path $Rec "terminal-evidence-$RunId.mp4"

$snap = Get-ChildItem -Path $Rec -Filter "mongo-snapshot-*.txt" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
$worker = Get-ChildItem -Path $Rec -Filter "term-worker-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $snap) { throw "No mongo-snapshot-*.txt in $Rec" }

$title = "EdgeGuard Ops MongoDB evidence"
$snapPath = $snap.FullName
$workerPath = if ($worker) { $worker.FullName } else { "" }
$js = Join-Path $Repo "scripts\mongo-snapshot-e2e.js"

$ps1 = @"
`$Host.UI.RawUI.WindowTitle = '$title'
Set-Location '$Repo'
try { `$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(180, 90) } catch {}
Clear-Host
Write-Host '=== EdgeGuard Ops — MongoDB evidence (automatic E2E 20261021183352) ===' -ForegroundColor Cyan
Write-Host 'Keyed by Mongo _id: db.devices.findOne({_id:\"edge-001\"})'
Write-Host 'Incident inc-thermal-edge-001-20261021113510'
Write-Host ''
Get-Content -LiteralPath '$snapPath'
Write-Host ''
Write-Host '=== Live mongosh snapshot ===' -ForegroundColor Cyan
docker cp '$js' edgeguard-ops-mongodb-1:/tmp/mongo-snapshot-e2e.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-snapshot-e2e.js
Write-Host ''
if (Test-Path -LiteralPath '$workerPath') {
  Write-Host '=== Response worker (Remediation applied / RECOVERING / RESOLVED) ===' -ForegroundColor Cyan
  Select-String -LiteralPath '$workerPath' -Pattern 'Remediation applied|RECOVERING|RESOLVED|commanded_profile' |
    Select-Object -Last 15 |
    ForEach-Object { `$_.Line }
}
Write-Host ''
Write-Host 'Hold for recording...' -ForegroundColor Yellow
Start-Sleep -Seconds 55
"@

$term = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit","-NoProfile","-Command", $ps1) -PassThru -WindowStyle Maximized
Start-Sleep -Seconds 10
try {
  Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Fg { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd); }'
  [Fg]::SetForegroundWindow($term.MainWindowHandle) | Out-Null
} catch {}
Start-Sleep -Seconds 2

$ffArgs = @(
  "-y", "-f", "gdigrab", "-framerate", "30",
  "-i", "title=$title",
  "-t", "48",
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22",
  "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
  $Out
)
Write-Host "Recording terminal evidence -> $Out (window title=$title)"
& ffmpeg @ffArgs
$ffExit = $LASTEXITCODE
if ($ffExit -ne 0 -or -not (Test-Path $Out) -or ((Get-Item $Out).Length -lt 50000)) {
    Write-Host "TITLE_GRAB_FAILED — not falling back to full desktop (avoids unrelated windows)"
    Stop-Process -Id $term.Id -Force -ErrorAction SilentlyContinue
    exit 4
}
Write-Host "DONE_TERMINAL" $Out ((Get-Item $Out).Length)
Stop-Process -Id $term.Id -Force -ErrorAction SilentlyContinue
