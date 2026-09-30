from edgeguard_simulator.models import DeviceConfig, ScenarioName, TelemetrySample
from edgeguard_simulator.scenarios import scenario_for


class TelemetryGenerator:
    """Placeholder generator. It does not emit synthetic readings yet."""

    def next_sample(self, device: DeviceConfig, scenario: ScenarioName) -> TelemetrySample:
        # TODO(build-window): build a baseline sample, then let the scenario mutate it.
        return scenario_for(scenario).apply(_missing_baseline(device))


def _missing_baseline(device: DeviceConfig) -> TelemetrySample:
    raise NotImplementedError(
        f"Baseline telemetry for {device.device_id} is not implemented. "
        "Implement the simulator during 2026-10-10 to 2026-10-24."
    )
