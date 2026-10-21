#!/usr/bin/env python3
"""
Record authentic Datadog UI with Playwright (persistent profile + system Chrome).
ONE manual login if needed — never bypasses auth; never prints secrets.

Waits until timeseries graphs and the logs list have real content before
the interactive portion of the recording. Does not scroll the monitor past
its status header.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

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
    print("WAITING_FOR_LOGIN: complete Datadog auth/MFA in the opened Chrome window.", flush=True)
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


def wait_dashboard_ready(page, timeout_s: int = 90) -> dict:
    """Poll until graphs have paths and the logs widget is not an empty search icon."""
    deadline = time.time() + timeout_s
    last = {"svg_paths": 0, "log_rows": 0, "spinners": 99}
    while time.time() < deadline:
        last = page.evaluate(
            """() => {
              const paths = document.querySelectorAll('svg path, svg polyline, canvas').length;
              const spinners = document.querySelectorAll(
                '[class*="Spinner"], [class*="spinner"], [class*="LoadingSpinner"]'
              ).length;
              const body = document.body ? document.body.innerText : '';
              const hasGpu = /GPU temperature/i.test(body);
              const hasLogsTitle = /Incident and remediation logs/i.test(body);
              const emptyLogs = /No matching logs|No logs found|Add.*Widgets or/i.test(body)
                && !/RESOLVED|RECOVERING|Remediation applied|thermal/i.test(body);
              const logHits = (body.match(/RESOLVED|RECOVERING|Remediation applied|thermal_throttling/gi) || []).length;
              return { svg_paths: paths, spinners, hasGpu, hasLogsTitle, emptyLogs, logHits };
            }"""
        )
        print("  dash_ready", last, flush=True)
        if last.get("hasGpu") and last.get("svg_paths", 0) >= 8 and last.get("spinners", 99) <= 1:
            if last.get("logHits", 0) >= 1 or not last.get("emptyLogs", True):
                print("DASHBOARD_READY", last, flush=True)
                return last
            # Graphs loaded; give logs a bit more time but do not loop forever.
            if time.time() + 8 > deadline:
                print("DASHBOARD_GRAPHS_READY_LOGS_UNCERTAIN", last, flush=True)
                return last
        page.wait_for_timeout(2500)
    print("DASHBOARD_WAIT_TIMEOUT", last, flush=True)
    return last


def wait_monitor_status(page, timeout_s: int = 40) -> dict:
    deadline = time.time() + timeout_s
    last = {"tokens": []}
    while time.time() < deadline:
        last = page.evaluate(
            """() => {
              const body = document.body ? document.body.innerText : '';
              const tokens = ['OK','Alert','ALERT','Warn','No Data','Triggered'].filter(t => body.includes(t));
              const svg = document.querySelectorAll('svg path, canvas').length;
              return { tokens, svg, hasName: /GPU thermal|EdgeGuard/i.test(body) };
            }"""
        )
        print("  monitor_ready", last, flush=True)
        if last.get("hasName") and last.get("tokens"):
            print("MONITOR_READY", last, flush=True)
            return last
        page.wait_for_timeout(2000)
    print("MONITOR_WAIT_TIMEOUT", last, flush=True)
    return last


def record_sequence(context, page, meta: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    print("WAIT dashboard...", flush=True)
    page.goto(DASHBOARD, wait_until="domcontentloaded", timeout=180000)
    meta["dashboard_ready"] = wait_dashboard_ready(page)
    page.wait_for_timeout(1500)
    print("REC dashboard (widgets loaded)...", flush=True)
    try:
        page.screenshot(path=str(OUT / "still-dashboard.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot dashboard skip:", type(e).__name__, flush=True)

    # Interact: hover graphs, scroll to logs (not past them into empty chrome)
    for x, y in ((520, 260), (980, 260), (1440, 260), (520, 560), (980, 560), (1440, 560)):
        page.mouse.move(x, y)
        page.wait_for_timeout(1400)
    page.mouse.wheel(0, 420)
    page.wait_for_timeout(3500)
    page.mouse.move(900, 720)
    page.wait_for_timeout(2500)
    page.mouse.wheel(0, 280)
    page.wait_for_timeout(4000)
    try:
        page.screenshot(path=str(OUT / "still-dashboard-logs.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot logs skip:", type(e).__name__, flush=True)
    meta["dashboard_url"] = page.url

    print("REC monitor...", flush=True)
    page.goto(MONITOR, wait_until="domcontentloaded", timeout=180000)
    page.wait_for_timeout(3500)
    try:
        page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass
    meta["monitor_ready"] = wait_monitor_status(page)
    try:
        page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass
    page.wait_for_timeout(4000)
    try:
        page.screenshot(path=str(OUT / "still-monitor.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot monitor skip:", type(e).__name__, flush=True)
    try:
        body = page.inner_text("body")[:4000]
    except Exception:
        body = ""
    meta["monitor_body_snippet"] = body[:900]
    for token in ("Alert", "ALERT", "OK", "Warn", "No Data", "Triggered", "Resolved"):
        if token.lower() in body.lower():
            meta.setdefault("monitor_tokens_seen", []).append(token)
    # Keep the OK status header in frame; do not scroll into Event Timeline.
    page.wait_for_timeout(14000)
    print("REC sequence complete", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record-only", action="store_true")
    ap.add_argument("--login-timeout", type=int, default=600)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    PROFILE.mkdir(parents=True, exist_ok=True)
    meta: dict = {"dashboard": DASHBOARD, "monitor": MONITOR}

    video_dir = OUT / "pw-video"
    video_dir.mkdir(parents=True, exist_ok=True)
    for old in video_dir.glob("*.webm"):
        old.unlink(missing_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="chrome",
            headless=False,
            viewport=VIEWPORT,
            record_video_dir=str(video_dir),
            record_video_size=VIEWPORT,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.set_viewport_size(VIEWPORT)
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

        record_sequence(context, page, meta)
        context.close()

    videos = sorted(video_dir.glob("*.webm"))
    meta["videos"] = [str(v.relative_to(ROOT)).replace("\\", "/") for v in videos]
    meta["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT / "datadog-capture-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("DONE videos=", len(videos), flush=True)
    for v in videos:
        print(" ", v, v.stat().st_size, flush=True)
    return 0 if videos else 3


if __name__ == "__main__":
    raise SystemExit(main())
