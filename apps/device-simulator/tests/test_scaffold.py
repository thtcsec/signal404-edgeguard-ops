import pytest

from edgeguard_simulator.config import SimulatorConfig
from edgeguard_simulator.generator import TelemetryGenerator
from edgeguard_simulator.models import DeviceConfig, ScenarioName
from edgeguard_simulator.scenarios import scenario_for


def test_scenario_names() -> None:
    assert {item.value for item in ScenarioName} == {
        "NORMAL",
        "THERMAL_THROTTLE",
        "NETWORK_DEGRADATION",
        "MEMORY_PRESSURE",
    }


def test_generator_is_not_implemented() -> None:
    device = DeviceConfig(
        device_id="edge-001",
        name="Factory Camera 01",
        site="factory-a",
        line="line-03",
    )
    with pytest.raises(NotImplementedError):
        TelemetryGenerator().next_sample(device, ScenarioName.NORMAL)


def test_scenario_hook_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        scenario_for(ScenarioName.THERMAL_THROTTLE).apply(None)  # type: ignore[arg-type]


def test_config_defaults_do_not_embed_secrets() -> None:
    config = SimulatorConfig.from_env()
    assert "api_key" not in config.telemetry_url.lower()
    assert config.device_count >= 1
