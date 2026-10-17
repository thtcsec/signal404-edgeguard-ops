# device-simulator

Python 3.11 synthetic IoT fleet simulator. No real camera streams. Standard library only at runtime.

## Scenarios

| Name | Behavior |
| --- | --- |
| `NORMAL` | Stable healthy telemetry |
| `THERMAL_THROTTLE` | Temperature rises → latency up, FPS down; `safe` profile recovers |
| `NETWORK_DEGRADATION` | Packet loss and network latency rise |
| `MEMORY_PRESSURE` | Memory and inference latency rise |

## Run

```powershell
python -m pip install -r requirements.txt
python -m pytest

$env:EDGEGUARD_TELEMETRY_URL = "http://localhost:5080"
$env:EDGEGUARD_DEVICE_COUNT = "3"
$env:EDGEGUARD_INTERVAL_SECONDS = "1"
$env:EDGEGUARD_SCENARIO = "THERMAL_THROTTLE"
$env:PYTHONPATH = "src"
python -m edgeguard_simulator.main
```
