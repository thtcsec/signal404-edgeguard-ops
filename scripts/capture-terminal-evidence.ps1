# Record a visible mongosh + log tail session with ffmpeg gdigrab (fragmented MP4 so Force-kill still playable).
$ErrorActionPreference = "Stop"
$Repo = "D:\tu_projects\signal404-edgeguard-ops"
$Rec = Join-Path $Repo "docs\video\recordings"
$RunId = Get-Date -Format "yyyyMMddHHmmss"
$Out = Join-Path $Rec "terminal-evidence-$RunId.mp4"

# Open a large console showing mongo evidence (no secrets)
$ps1 = @"
`$Host.UI.RawUI.WindowTitle = 'EdgeGuard Ops — MongoDB evidence'
Set-Location '$Repo'
Clear-Host
Write-Host '=== EdgeGuard Ops — REAL MongoDB evidence (automatic E2E run) ===' -ForegroundColor Cyan
Write-Host 'Incident: inc-thermal-edge-001-20261019144446'
Write-Host ''
Get-Content '$Rec\mongo-snapshot-20261019214254.txt'
Write-Host ''
Write-Host '=== Response worker log (tail) ===' -ForegroundColor Cyan
Get-Content '$Rec\term-worker-20261019214254.log' -Tail 40
Write-Host ''
Write-Host '=== Simulator log (tail) ===' -ForegroundColor Cyan
Get-Content '$Rec\term-sim-20261019214254.log' -Tail 30
Write-Host ''
Write-Host 'Hold for recording...' -ForegroundColor Yellow
Start-Sleep -Seconds 45
"@
$arg = "-NoExit -NoProfile -Command $ps1"
$term = Start-Process -FilePath "powershell.exe" -ArgumentList $arg -PassThru -WindowStyle Maximized
Start-Sleep -Seconds 3

# Fragmented MP4 survives abrupt stop
$ffArgs = @(
  "-y", "-f", "gdigrab", "-framerate", "30", "-offset_x", "0", "-offset_y", "0",
  "-video_size", "1920x1080", "-i", "desktop",
  "-t", "40",
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22",
  "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
  $Out
)
Write-Host "Recording terminal evidence -> $Out"
& ffmpeg @ffArgs
Write-Host "DONE_TERMINAL" $Out ((Get-Item $Out).Length)
Stop-Process -Id $term.Id -Force -ErrorAction SilentlyContinue
