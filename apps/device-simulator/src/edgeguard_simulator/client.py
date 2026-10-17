from __future__ import annotations

import json
import urllib.error
import urllib.request

from edgeguard_simulator.models import TelemetrySample


class TelemetryClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._ingest_url = base_url.rstrip("/") + "/telemetry"
        self._timeout = timeout_seconds

    def post(self, sample: TelemetrySample) -> int:
        body = json.dumps(sample.to_payload()).encode("utf-8")
        request = urllib.request.Request(
            self._ingest_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return int(response.status)
        except urllib.error.HTTPError as error:
            return int(error.code)
