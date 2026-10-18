#!/usr/bin/env python3
"""Fetch authentic Datadog graph snapshots for the verified incident window. Never prints secrets."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "video" / "captures"
OUT.mkdir(parents=True, exist_ok=True)


def load_env() -> dict[str, str]:
    vals: dict[str, str] = {}
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def download_snapshot_png(snap_url: str, dest: Path, timeout_s: int = 120) -> bool:
    """Poll Datadog public snapshot until PNG is ready."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        req = urllib.request.Request(snap_url)
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            ctype = (r.headers.get("Content-Type") or "").lower()
        if "json" in ctype or body[:1] == b"{":
            try:
                status = json.loads(body).get("data", {}).get("attributes", {}).get("status")
            except Exception:
                status = "unknown"
            print("  pending status=", status)
            time.sleep(2)
            continue
        if body[:8] == b"\x89PNG\r\n\x1a\n" or "image" in ctype or len(body) > 1000:
            dest.write_bytes(body)
            print("  wrote", dest.name, len(body))
            return True
        time.sleep(2)
    print("  TIMEOUT waiting for PNG")
    return False


def main() -> None:
    vals = load_env()
    api = vals.get("DD_API_KEY") or os.environ.get("DD_API_KEY")
    app = vals.get("DD_APP_KEY") or os.environ.get("DD_APP_KEY")
    site = vals.get("DD_SITE") or os.environ.get("DD_SITE") or "datadoghq.com"
    print("keys_present", bool(api and len(api) > 20), bool(app and len(app) > 20), "site", site)
    if not (api and app):
        print("NO_KEYS")
        return

    start = int(datetime(2026, 10, 18, 8, 48, 0, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 10, 18, 8, 55, 0, tzinfo=timezone.utc).timestamp())
    queries = {
        "gpu": "avg:edgeguard.device.gpu_temperature{*}",
        "latency": "avg:edgeguard.device.inference_latency{*}",
        "fps": "avg:edgeguard.device.fps{*}",
        "gpu-edge001": "avg:edgeguard.device.gpu_temperature{device_id:edge-001}",
        "latency-edge001": "avg:edgeguard.device.inference_latency{device_id:edge-001}",
        "fps-edge001": "avg:edgeguard.device.fps{device_id:edge-001}",
    }

    meta = []
    headers = {"DD-API-KEY": api, "DD-APPLICATION-KEY": app}
    for name, q in queries.items():
        params = urllib.parse.urlencode(
            {"metric_query": q, "start": start, "end": end, "title": f"EdgeGuard {name} historical"}
        )
        url = f"https://api.{site}/api/v1/graph/snapshot?{params}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode())
            snap = data.get("snapshot_url")
            print(name, "snap_url", bool(snap))
            if not snap:
                continue
            path = OUT / f"datadog-graph-{name}.png"
            ok = download_snapshot_png(snap, path)
            if ok:
                meta.append({"name": name, "file": path.name, "bytes": path.stat().st_size, "query": q, "snapshot_url": snap})
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")[:200]
            print(name, "HTTP", e.code, body)
        except Exception as e:
            print(name, "ERR", type(e).__name__, str(e)[:160])

    try:
        murl = f"https://api.{site}/api/v1/monitor/333934695"
        req = urllib.request.Request(murl, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            mon = json.loads(resp.read().decode())
        state = {
            "id": mon.get("id"),
            "overall_state": mon.get("overall_state"),
            "name": mon.get("name"),
            "overall_state_modified": mon.get("overall_state_modified"),
        }
        print("monitor_overall_state", state["overall_state"])
        (OUT / "monitor-status.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        print("monitor_ERR", type(e).__name__, str(e)[:160])

    (OUT / "captures-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("DONE", len(meta), "graphs")


if __name__ == "__main__":
    main()
