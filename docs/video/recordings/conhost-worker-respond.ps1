$Host.UI.RawUI.WindowTitle = 'EG-Respond-Worker'
. 'D:\tu_projects\signal404-edgeguard-ops\scripts\set-console-font.ps1'
try { $Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
try { $Host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(150, 40) } catch {}
Clear-Host
Write-Host 'RESPOND  ·  response-worker log  ·  E2E 20261021202014' -ForegroundColor Yellow
Write-Host 'Authentic lines from term-worker-20261021200755.log — this run' -ForegroundColor DarkGray
Write-Host 'incident inc-thermal-edge-001-20261021132057' -ForegroundColor DarkGray
Write-Host ''
Start-Sleep -Seconds 4
Write-Host '20:21:02  Remediation applied incident_id=inc-thermal-edge-001-20261021132057 device_id=edge-001 action_id=act-safe-edge-001-20261021132102 commanded_profile=safe' -ForegroundColor Yellow
Start-Sleep -Seconds 2
Write-Host '20:21:07  Incident entered RECOVERING incident_id=inc-thermal-edge-001-20261021132057 device_id=edge-001 observation_seconds=20' -ForegroundColor Cyan
Start-Sleep -Seconds 2
Write-Host '20:21:27  Incident RESOLVED incident_id=inc-thermal-edge-001-20261021132057 device_id=edge-001 action_id=act-safe-edge-001-20261021132102 reason=Continuous healthy reported-safe telemetry verified.' -ForegroundColor Green
Write-Host ''
Write-Host 'Mongo  incident.status=RESOLVED  remediation.state=VERIFIED' -ForegroundColor Cyan
Start-Sleep -Seconds 3
