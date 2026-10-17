$ErrorActionPreference = "Stop"
Write-Host "Prefer the Python simulator for seeding synthetic telemetry:"
Write-Host '  cd apps/device-simulator'
Write-Host '  $env:PYTHONPATH = "src"'
Write-Host '  $env:EDGEGUARD_SCENARIO = "NORMAL"'
Write-Host '  python -m edgeguard_simulator.main'
exit 0
