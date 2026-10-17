from dataclasses import dataclass, replace
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

    def _replace(self, **kwargs: object) -> "TelemetrySample":
        return replace(self, **kwargs)

    def to_payload(self) -> dict[str, object]:
        return {
            "deviceId": self.device_id,
            "site": self.site,
            "line": self.line,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "cpuUsage": self.cpu_usage,
            "memoryUsage": self.memory_usage,
            "cpuTemperature": self.cpu_temperature,
            "gpuTemperature": self.gpu_temperature,
            "gpuUsage": self.gpu_usage,
            "fps": self.fps,
            "inferenceLatencyMs": self.inference_latency_ms,
            "packetLossPct": self.packet_loss_pct,
            "networkLatencyMs": self.network_latency_ms,
            "droppedFrames": self.dropped_frames,
            "profile": self.profile,
            "status": self.status,
        }
