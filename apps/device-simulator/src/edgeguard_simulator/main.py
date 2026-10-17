from __future__ import annotations

import signal
import sys
import time

from edgeguard_simulator.client import TelemetryClient
from edgeguard_simulator.config import SimulatorConfig
from edgeguard_simulator.generator import TelemetryGenerator
from edgeguard_simulator.models import DeviceConfig, ScenarioName


def build_devices(count: int) -> list[DeviceConfig]:
    devices: list[DeviceConfig] = []
    for index in range(1, count + 1):
        device_id = f"edge-{index:03d}"
        devices.append(
            DeviceConfig(
                device_id=device_id,
                name=f"Factory Camera {index:02d}",
                site="factory-a",
                line=f"line-{(index % 3) + 1:02d}",
            )
        )
    return devices


def parse_scenario(raw: str) -> ScenarioName:
    try:
        return ScenarioName(raw.strip().upper())
    except ValueError as error:
        raise SystemExit(
            f"Unknown scenario '{raw}'. Use NORMAL, THERMAL_THROTTLE, "
            "NETWORK_DEGRADATION, or MEMORY_PRESSURE."
        ) from error


def main() -> int:
    config = SimulatorConfig.from_env()
    scenario = parse_scenario(config.scenario)
    devices = build_devices(config.device_count)
    generator = TelemetryGenerator(seed=404)
    client = TelemetryClient(config.telemetry_url)
    # Local applied profile cache, synced from commanded profile.
    applied_profiles: dict[str, str] = {device.device_id: "full" for device in devices}
    stop = False

    def _handle_stop(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _handle_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_stop)

    print(
        "EdgeGuard simulator started "
        f"scenario={scenario.value} devices={len(devices)} "
        f"url={config.telemetry_url} interval={config.interval_seconds}s",
        flush=True,
    )

    while not stop:
        for device in devices:
            commanded = client.get_commanded_profile(
                device.device_id, default=applied_profiles[device.device_id]
            )
            applied_profiles[device.device_id] = commanded
            sample = generator.next_sample(device, scenario, profile=commanded)
            result = client.post(sample)
            if result.commanded_profile in {"full", "reduced", "safe"}:
                applied_profiles[device.device_id] = result.commanded_profile
            print(
                f"{sample.timestamp.isoformat()} {device.device_id} "
                f"gpu={sample.gpu_temperature:.1f}C fps={sample.fps:.1f} "
                f"lat={sample.inference_latency_ms:.1f}ms status={sample.status} "
                f"reported_profile={sample.profile} commanded_profile={applied_profiles[device.device_id]} "
                f"http={result.http_status}",
                flush=True,
            )
        time.sleep(config.interval_seconds)

    print("Simulator stopped.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
