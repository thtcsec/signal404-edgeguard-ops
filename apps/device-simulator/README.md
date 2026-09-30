# device-simulator

Python 3.11 scaffold for a future synthetic IoT fleet.

Planned scenarios: `NORMAL`, `THERMAL_THROTTLE`, `NETWORK_DEGRADATION`, `MEMORY_PRESSURE`.

`python -m edgeguard_simulator.main` prints the scaffold status and exits with code 2. It does not open sockets and does not generate telemetry.

```powershell
python -m pip install -r requirements.txt
python -m pytest
```

Run commands from this directory, or set `PYTHONPATH` to `src` when launching the module from elsewhere.
