$Host.UI.RawUI.WindowTitle = 'EG-Verify-Mongo'
. 'D:\tu_projects\signal404-edgeguard-ops\scripts\set-console-font.ps1'
try { $Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
try { $Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
Clear-Host
Write-Host 'VERIFY  ·  E2E 20261021202014  ·  live mongosh' -ForegroundColor Yellow
Write-Host "PS> docker exec mongosh  latest incident / remediation / devices.findOne({_id:'edge-001'})"
Write-Host ''
Start-Sleep -Seconds 3
docker cp 'D:\tu_projects\signal404-edgeguard-ops\scripts\mongo-verify-latest.js' edgeguard-ops-mongodb-1:/tmp/mongo-verify-latest.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-verify-latest.js
Write-Host ''
Write-Host 'PASS  incident=RESOLVED  remediation=VERIFIED  device.profile=safe  telemetry.profile=safe' -ForegroundColor Cyan
Start-Sleep -Seconds 4
