$Host.UI.RawUI.WindowTitle = "EG Inject Fault"
. "D:\tu_projects\signal404-edgeguard-ops\scripts\set-console-font.ps1"
try { $Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
try { $Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(160, 45) } catch {}
Clear-Host
Write-Host "INJECT FAULT  ·  EdgeGuard device simulator" -ForegroundColor Yellow
Write-Host "Automatic E2E used EDGEGUARD_SCENARIO=THERMAL_THROTTLE" -ForegroundColor DarkGray
Write-Host ""
Set-Location "D:\tu_projects\signal404-edgeguard-ops\apps\device-simulator"
$env:PYTHONPATH = "src"
$env:EDGEGUARD_TELEMETRY_URL = "http://localhost:5080"
$env:EDGEGUARD_DEVICE_COUNT = "1"
$env:EDGEGUARD_INTERVAL_SECONDS = "1"
$env:EDGEGUARD_SCENARIO = "THERMAL_THROTTLE"
Write-Host "PS apps\device-simulator>" -NoNewline
Write-Host " `$env:EDGEGUARD_SCENARIO='THERMAL_THROTTLE'; python -m edgeguard_simulator.main" -ForegroundColor White
Write-Host ""
python -m edgeguard_simulator.main
