import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulatorConfig:
    """Runtime settings. Fault timing and device fleets are not implemented yet."""

    telemetry_url: str
    device_count: int
    interval_seconds: float
    scenario: str

    @staticmethod
    def from_env() -> "SimulatorConfig":
        return SimulatorConfig(
            telemetry_url=os.environ.get("EDGEGUARD_TELEMETRY_URL", "http://localhost:5080"),
            device_count=int(os.environ.get("EDGEGUARD_DEVICE_COUNT", "1")),
            interval_seconds=float(os.environ.get("EDGEGUARD_INTERVAL_SECONDS", "1")),
            scenario=os.environ.get("EDGEGUARD_SCENARIO", "NORMAL"),
        )
