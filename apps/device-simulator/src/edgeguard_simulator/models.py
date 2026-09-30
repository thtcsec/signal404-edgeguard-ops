from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ScenarioName(str, Enum):
    NORMAL = "NORMAL"
    THERMAL_THROTTLE = "THERMAL_THROTTLE"
    NETWORK_DEGRADATION = "NETWORK_DEGRADATION"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"


@dataclass(frozen=True)
class DeviceConfig:
    device_id: str
    name: str
    site: str
    line: str
    device_type: str = "edge-camera"


@dataclass(frozen=True)
class TelemetrySample:
    timestamp: datetime
    device_id: str
    site: str
    line: str
    cpu_usage: float
    memory_usage: float
    cpu_temperature: float
    gpu_temperature: float
    gpu_usage: float
    fps: float
    inference_latency_ms: float
    packet_loss_pct: float
    network_latency_ms: float
    dropped_frames: int
    profile: str
    status: str
