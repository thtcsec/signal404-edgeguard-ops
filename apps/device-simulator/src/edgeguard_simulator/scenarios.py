from __future__ import annotations

import math
import random
from typing import Protocol

from edgeguard_simulator.models import ScenarioName, TelemetrySample


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def wave(tick: int, period: int = 60) -> float:
    return 0.5 + 0.5 * math.sin((2.0 * math.pi * tick) / period)


class Scenario(Protocol):
    name: ScenarioName

    def apply(
        self,
        sample: TelemetrySample,
        tick: int,
        rng: random.Random,
    ) -> TelemetrySample: ...


class NormalScenario:
    name = ScenarioName.NORMAL

    def apply(
        self,
        sample: TelemetrySample,
        tick: int,
        rng: random.Random,
    ) -> TelemetrySample:
        return sample


class ThermalThrottleScenario:
    """Ramps temperature until latency/FPS degrade; respects safe profile recovery."""

    name = ScenarioName.THERMAL_THROTTLE

    def apply(
        self,
        sample: TelemetrySample,
        tick: int,
        rng: random.Random,
    ) -> TelemetrySample:
        if sample.profile == "safe":
            return sample._replace(
                cpu_temperature=round(clamp(sample.cpu_temperature - 8.0 + rng.uniform(-1, 1), 45, 70), 2),
                gpu_temperature=round(clamp(sample.gpu_temperature - 10.0 + rng.uniform(-1, 1), 48, 72), 2),
                fps=round(clamp(sample.fps + 4.0, 18, 32), 2),
                inference_latency_ms=round(clamp(sample.inference_latency_ms - 25.0, 20, 80), 2),
                dropped_frames=max(0, sample.dropped_frames - 5),
                status="healthy",
            )

        # Progressive heat: mild for ~20s, then throttle zone.
        heat = min(tick / 25.0, 1.0)
        oscillation = wave(tick, period=40)
        gpu_temp = sample.gpu_temperature + (28.0 * heat) + (3.0 * oscillation)
        cpu_temp = sample.cpu_temperature + (22.0 * heat) + (2.0 * oscillation)
        latency = sample.inference_latency_ms + (140.0 * heat)
        fps = sample.fps - (18.0 * heat)
        dropped = sample.dropped_frames + int(30 * heat)

        degraded = gpu_temp >= 85.0 or latency >= 120.0 or fps <= 15.0
        return sample._replace(
            cpu_temperature=round(clamp(cpu_temp, 50, 105), 2),
            gpu_temperature=round(clamp(gpu_temp, 55, 110), 2),
            gpu_usage=round(clamp(sample.gpu_usage + 10.0 * heat, 40, 99), 2),
            inference_latency_ms=round(clamp(latency, 20, 260), 2),
            fps=round(clamp(fps, 4, 32), 2),
            dropped_frames=max(0, dropped),
            status="degraded" if degraded else "healthy",
            profile=sample.profile,
        )


class NetworkDegradationScenario:
    name = ScenarioName.NETWORK_DEGRADATION

    def apply(
        self,
        sample: TelemetrySample,
        tick: int,
        rng: random.Random,
    ) -> TelemetrySample:
        severity = min(tick / 30.0, 1.0)
        return sample._replace(
            packet_loss_pct=round(clamp(0.2 + 8.0 * severity + rng.uniform(0, 0.5), 0, 20), 3),
            network_latency_ms=round(clamp(sample.network_latency_ms + 120.0 * severity, 10, 400), 2),
            fps=round(clamp(sample.fps - 10.0 * severity, 5, 32), 2),
            dropped_frames=sample.dropped_frames + int(20 * severity),
            status="degraded" if severity > 0.4 else "healthy",
        )


class MemoryPressureScenario:
    name = ScenarioName.MEMORY_PRESSURE

    def apply(
        self,
        sample: TelemetrySample,
        tick: int,
        rng: random.Random,
    ) -> TelemetrySample:
        severity = min(tick / 35.0, 1.0)
        return sample._replace(
            memory_usage=round(clamp(sample.memory_usage + 35.0 * severity, 40, 98), 2),
            inference_latency_ms=round(clamp(sample.inference_latency_ms + 90.0 * severity, 20, 220), 2),
            fps=round(clamp(sample.fps - 12.0 * severity, 5, 32), 2),
            status="degraded" if severity > 0.5 else "healthy",
        )


_SCENARIOS: dict[ScenarioName, Scenario] = {
    ScenarioName.NORMAL: NormalScenario(),
    ScenarioName.THERMAL_THROTTLE: ThermalThrottleScenario(),
    ScenarioName.NETWORK_DEGRADATION: NetworkDegradationScenario(),
    ScenarioName.MEMORY_PRESSURE: MemoryPressureScenario(),
}


def scenario_for(name: ScenarioName) -> Scenario:
    return _SCENARIOS[name]
