from __future__ import annotations

import random
from datetime import datetime, timezone

from edgeguard_simulator.models import DeviceConfig, ScenarioName, TelemetrySample
from edgeguard_simulator.scenarios import scenario_for


class TelemetryGenerator:
    """Deterministic-ish synthetic generator for fleet telemetry."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._tick = 0

    def next_sample(
        self,
        device: DeviceConfig,
        scenario: ScenarioName,
        profile: str = "full",
    ) -> TelemetrySample:
        self._tick += 1
        baseline = self._baseline(device, profile)
        return scenario_for(scenario).apply(baseline, self._tick, self._rng)

    def _baseline(self, device: DeviceConfig, profile: str) -> TelemetrySample:
        profile_factor = {"full": 1.0, "reduced": 0.7, "safe": 0.45}.get(profile, 1.0)
        jitter = self._rng.uniform(-1.5, 1.5)

        cpu_temp = 58.0 + jitter
        gpu_temp = 64.0 + jitter
        fps = 30.0 * profile_factor + self._rng.uniform(-0.4, 0.4)
        latency = (38.0 / max(profile_factor, 0.3)) + self._rng.uniform(-2.0, 2.0)

        return TelemetrySample(
            timestamp=datetime.now(timezone.utc),
            device_id=device.device_id,
            site=device.site,
            line=device.line,
            cpu_usage=round(35.0 + 8.0 * profile_factor + self._rng.uniform(-2, 2), 2),
            memory_usage=round(50.0 + 10.0 * profile_factor + self._rng.uniform(-2, 2), 2),
            cpu_temperature=round(cpu_temp, 2),
            gpu_temperature=round(gpu_temp, 2),
            gpu_usage=round(55.0 + 25.0 * profile_factor + self._rng.uniform(-3, 3), 2),
            fps=round(max(fps, 1.0), 2),
            inference_latency_ms=round(max(latency, 5.0), 2),
            packet_loss_pct=round(max(0.0, self._rng.uniform(0.0, 0.3)), 3),
            network_latency_ms=round(10.0 + self._rng.uniform(-1.5, 1.5), 2),
            dropped_frames=max(0, int(self._rng.uniform(0, 2))),
            profile=profile,
            status="healthy",
        )
