from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from edgeguard_simulator.models import TelemetrySample


@dataclass(frozen=True)
class IngestResult:
    http_status: int
    commanded_profile: str | None
    reported_profile: str | None


class TelemetryClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def get_commanded_profile(self, device_id: str, default: str = "full") -> str:
        request = urllib.request.Request(
            f"{self._base_url}/devices/{device_id}",
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                # Prefer commandedProfile; fall back to legacy "profile" during rollout.
                profile = str(
                    payload.get("commandedProfile") or payload.get("profile") or default
                ).lower()
                return profile if profile in {"full", "reduced", "safe"} else default
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return default
            return default
        except Exception:
            return default

    def post(self, sample: TelemetrySample) -> IngestResult:
        body = json.dumps(sample.to_payload()).encode("utf-8")
        request = urllib.request.Request(
            f"{self._base_url}/telemetry",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                commanded = payload.get("commandedProfile") or payload.get("profile")
                reported = payload.get("reportedProfile")
                return IngestResult(
                    http_status=int(response.status),
                    commanded_profile=str(commanded).lower() if commanded else None,
                    reported_profile=str(reported).lower() if reported else None,
                )
        except urllib.error.HTTPError as error:
            return IngestResult(http_status=int(error.code), commanded_profile=None, reported_profile=None)
