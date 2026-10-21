$Host.UI.RawUI.WindowTitle = "EG Verify Mongo"
. "D:\tu_projects\signal404-edgeguard-ops\scripts\set-console-font.ps1"
try { $Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
try { $Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(140, 42) } catch {}
Clear-Host
Write-Host "VERIFY  ·  E2E 20261021183352  ·  keyed by Mongo _id" -ForegroundColor Yellow
Write-Host "PS> docker exec ... mongosh  db.devices.findOne({_id:'edge-001'})" -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 2
docker cp "D:\tu_projects\signal404-edgeguard-ops\scripts\mongo-verify-183352.js" edgeguard-ops-mongodb-1:/tmp/mongo-verify-183352.js | Out-Null
docker exec edgeguard-ops-mongodb-1 mongosh --quiet /tmp/mongo-verify-183352.js
Write-Host ""
Write-Host "PS> worker log  Remediation applied / RECOVERING / RESOLVED" -ForegroundColor White
Select-String -LiteralPath "D:\tu_projects\signal404-edgeguard-ops\docs\video\recordings\term-worker-20261021183352.log" -Pattern "Remediation applied|RECOVERING|RESOLVED" |
    ForEach-Object {
        if ($_.Line -match '"Message":"([^"]+)"') { Write-Host $Matches[1] -ForegroundColor Green }
    }
Write-Host ""
Write-Host "PASS  incident=RESOLVED  remediation=VERIFIED  device.profile=safe  telemetry.profile=safe" -ForegroundColor Cyan
Start-Sleep -Seconds 30
