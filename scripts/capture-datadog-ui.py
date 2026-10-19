#!/usr/bin/env python3
"""
Record authentic Datadog UI with Playwright (persistent profile).
ONE manual login if needed — never bypasses auth; never prints secrets.

Usage:
  python scripts/capture-datadog-ui.py              # interactive: wait for login then record
  python scripts/capture-datadog-ui.py --record-only  # profile already authenticated
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "video" / "recordings"
PROFILE = ROOT / "docs" / "video" / ".dd-browser-profile"
DASHBOARD = "https://app.datadoghq.com/dashboard/9rr-a4u-2st"
MONITOR = "https://app.datadoghq.com/monitors/333934695"
VIEWPORT = {"width": 1920, "height": 1080}


def is_logged_in(page) -> bool:
    url = (page.url or "").lower()
    if "account/login" in url or "/login" in url:
        return False
    return "datadoghq.com" in url


def wait_for_login(page, timeout_s: int = 600) -> None:
    print("WAITING_FOR_LOGIN: complete Datadog auth/MFA in the opened Chromium window.", flush=True)
    print(f"  Target after login: {DASHBOARD}", flush=True)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            url = page.url or ""
        except Exception:
            time.sleep(2)
            continue
        print(f"  poll url={url[:100]}", flush=True)
        if is_logged_in(page):
            print("LOGIN_OK", url[:100], flush=True)
            return
        time.sleep(2)
    raise SystemExit("LOGIN_TIMEOUT: Datadog authentication not completed.")


def record_sequence(context, meta: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    page = context.new_page()
    page.set_viewport_size(VIEWPORT)

    print("REC dashboard...", flush=True)
    page.goto(DASHBOARD, wait_until="domcontentloaded", timeout=180000)
    # Wait for timeseries widgets to paint (avoid spinner-only footage)
    print("  waiting for widgets...", flush=True)
    page.wait_for_timeout(25000)
    for y in (200, 500, 900, 1200, 400):
        page.mouse.wheel(0, 450)
        page.wait_for_timeout(2200)
        try:
            page.evaluate(f"window.scrollTo(0, {y})")
        except Exception:
            pass
        page.wait_for_timeout(2500)
    try:
        page.screenshot(path=str(OUT / "still-dashboard.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot dashboard skip:", type(e).__name__, flush=True)
    meta["dashboard_url"] = page.url
    page.wait_for_timeout(4000)

    print("REC monitor...", flush=True)
    page.goto(MONITOR, wait_until="domcontentloaded", timeout=180000)
    page.wait_for_timeout(8000)
    for _ in range(4):
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
    try:
        page.screenshot(path=str(OUT / "still-monitor.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot monitor skip:", type(e).__name__, flush=True)
    try:
        body = page.inner_text("body")[:3000]
    except Exception:
        body = ""
    meta["monitor_body_snippet"] = body[:800]
    for token in ("Alert", "ALERT", "OK", "Warn", "No Data", "Triggered", "Resolved"):
        if token.lower() in body.lower():
            meta.setdefault("monitor_tokens_seen", []).append(token)
    page.wait_for_timeout(5000)

    print("REC dashboard return...", flush=True)
    page.goto(DASHBOARD, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(6000)
    page.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record-only", action="store_true")
    ap.add_argument("--login-timeout", type=int, default=600)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    PROFILE.mkdir(parents=True, exist_ok=True)
    meta: dict = {"dashboard": DASHBOARD, "monitor": MONITOR}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport=VIEWPORT,
            record_video_dir=str(OUT / "pw-video"),
            record_video_size=VIEWPORT,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        print("OPEN", DASHBOARD, flush=True)
        page.goto(DASHBOARD, wait_until="domcontentloaded", timeout=180000)
        page.wait_for_timeout(3000)
        print("URL", page.url[:120], flush=True)

        if not is_logged_in(page):
            if args.record_only:
                context.close()
                print("NOT_AUTHENTICATED", flush=True)
                return 2
            wait_for_login(page, args.login_timeout)
        else:
            print("SESSION_REUSED", page.url[:100], flush=True)

        record_sequence(context, meta)
        context.close()

    videos = sorted((OUT / "pw-video").glob("*.webm"))
    meta["videos"] = [str(v.relative_to(ROOT)).replace("\\", "/") for v in videos]
    meta["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT / "datadog-capture-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("DONE videos=", len(videos), flush=True)
    for v in videos:
        print(" ", v, v.stat().st_size, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
