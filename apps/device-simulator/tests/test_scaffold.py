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


def test_normal_generator_produces_healthy_sample() -> None:
    device = DeviceConfig(
        device_id="edge-001",
        name="Factory Camera 01",
        site="factory-a",
        line="line-03",
    )
    sample = TelemetryGenerator(seed=1).next_sample(device, ScenarioName.NORMAL)
    assert sample.device_id == "edge-001"
    assert sample.status == "healthy"
    assert 20 <= sample.fps <= 35
    assert sample.gpu_temperature < 80


def test_thermal_scenario_eventually_degrades() -> None:
    device = DeviceConfig(
        device_id="edge-001",
        name="Factory Camera 01",
        site="factory-a",
        line="line-03",
    )
    generator = TelemetryGenerator(seed=7)
    degraded = False
    for _ in range(40):
        sample = generator.next_sample(device, ScenarioName.THERMAL_THROTTLE)
        if sample.status == "degraded" and sample.gpu_temperature >= 85:
            degraded = True
            break
    assert degraded


def test_safe_profile_recovers_under_thermal_scenario() -> None:
    device = DeviceConfig(
        device_id="edge-001",
        name="Factory Camera 01",
        site="factory-a",
        line="line-03",
    )
    generator = TelemetryGenerator(seed=3)
    # Warm up into throttle territory first.
    for _ in range(30):
        generator.next_sample(device, ScenarioName.THERMAL_THROTTLE, profile="full")
    recovered = generator.next_sample(device, ScenarioName.THERMAL_THROTTLE, profile="safe")
    assert recovered.status == "healthy"
    assert recovered.gpu_temperature < 85


def test_config_defaults_do_not_embed_secrets() -> None:
    config = SimulatorConfig.from_env()
    assert "api_key" not in config.telemetry_url.lower()
    assert config.device_count >= 1


def test_scenario_registry_covers_all_names() -> None:
    for name in ScenarioName:
        assert scenario_for(name).name == name
