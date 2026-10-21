#!/usr/bin/env python3
"""
Record authentic Datadog UI with Playwright (persistent profile + system Chrome).
ONE manual login if needed — never bypasses auth; never prints secrets.

Locks the dashboard to an explicit from_ts/to_ts window for one E2E run.
Does not hover graphs (hover markers mix older events into the frame).
Skips the monitor Event Timeline unless --include-monitor is set.
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


def dashboard_url(from_ts: int | None, to_ts: int | None) -> str:
    if from_ts and to_ts:
        return (
            f"{DASHBOARD}?from_ts={from_ts}&to_ts={to_ts}"
            "&live=false&refresh_mode=paused&fromUser=true"
        )
    return DASHBOARD


def wait_dashboard_ready(page, timeout_s: int = 90, incident_id: str | None = None) -> dict:
    deadline = time.time() + timeout_s
    last: dict = {"svg_paths": 0, "log_rows": 0, "spinners": 99}
    needle = incident_id or ""
    while time.time() < deadline:
        last = page.evaluate(
            """(incidentNeedle) => {
              const paths = document.querySelectorAll('svg path, svg polyline, canvas').length;
              const spinners = document.querySelectorAll(
                '[class*="Spinner"], [class*="spinner"], [class*="LoadingSpinner"]'
              ).length;
              const body = document.body ? document.body.innerText : '';
              const hasGpu = /GPU temperature/i.test(body);
              const hasLogsTitle = /Incident and remediation logs/i.test(body);
              const emptyLogs = /No matching logs|No logs found/i.test(body)
                && !/RESOLVED|RECOVERING|Remediation applied|thermal/i.test(body);
              const logHits = (body.match(/RESOLVED|RECOVERING|Remediation applied|thermal_throttling/gi) || []).length;
              const incidentVisible = incidentNeedle ? body.includes(incidentNeedle) : true;
              const appliedVisible = /Remediation applied/i.test(body);
              const resolvedVisible = /Incident RESOLVED/i.test(body);
              return {
                svg_paths: paths, spinners, hasGpu, hasLogsTitle, emptyLogs,
                logHits, incidentVisible, appliedVisible, resolvedVisible
              };
            }""",
            needle,
        )
        print("  dash_ready", last, flush=True)
        graphs_ok = last.get("hasGpu") and last.get("svg_paths", 0) >= 8 and last.get("spinners", 99) <= 1
        logs_ok = last.get("logHits", 0) >= 1 or not last.get("emptyLogs", True)
        incident_ok = not needle or last.get("incidentVisible")
        if graphs_ok and logs_ok and incident_ok:
            print("DASHBOARD_READY", last, flush=True)
            return last
        if graphs_ok and time.time() + 10 > deadline:
            print("DASHBOARD_GRAPHS_READY_LOGS_UNCERTAIN", last, flush=True)
            return last
        page.wait_for_timeout(2500)
    print("DASHBOARD_WAIT_TIMEOUT", last, flush=True)
    return last


def record_sequence(page, meta: dict, args) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    url = dashboard_url(args.from_ts, args.to_ts)
    meta["dashboard_target"] = url
    print("WAIT dashboard...", url, flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=180000)
    meta["dashboard_ready"] = wait_dashboard_ready(page, incident_id=args.incident_id)
    page.wait_for_timeout(1200)
    print("REC dashboard (locked window, no graph hover)...", flush=True)
    try:
        page.screenshot(path=str(OUT / "still-dashboard.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot dashboard skip:", type(e).__name__, flush=True)

    # Stay on the loaded dashboard. Do not hover the left nav or timeseries
    # (nav flyouts and graph markers mix unrelated chrome into the frame).
    page.mouse.move(1100, 360)
    page.wait_for_timeout(4000)
    page.mouse.move(1100, 520)
    page.wait_for_timeout(5000)
    try:
        page.screenshot(path=str(OUT / "still-dashboard-logs.png"), full_page=False, timeout=10000)
    except Exception as e:
        print("screenshot logs skip:", type(e).__name__, flush=True)
    meta["dashboard_url"] = page.url
    page.wait_for_timeout(4000)
    print("REC dashboard complete", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record-only", action="store_true")
    ap.add_argument("--login-timeout", type=int, default=600)
    ap.add_argument("--from-ts", type=int, default=None, help="Dashboard window start, epoch ms")
    ap.add_argument("--to-ts", type=int, default=None, help="Dashboard window end, epoch ms")
    ap.add_argument("--incident-id", default=None)
    ap.add_argument("--include-monitor", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    PROFILE.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "dashboard": DASHBOARD,
        "from_ts": args.from_ts,
        "to_ts": args.to_ts,
        "incident_id": args.incident_id,
        "include_monitor": bool(args.include_monitor),
    }

    run_meta_path = OUT / "judge-e2e-run.json"
    if run_meta_path.is_file() and (args.from_ts is None or args.to_ts is None):
        run_meta = json.loads(run_meta_path.read_text(encoding="utf-8-sig"))
        args.from_ts = args.from_ts or run_meta.get("from_ts")
        args.to_ts = args.to_ts or run_meta.get("to_ts")
        args.incident_id = args.incident_id or run_meta.get("incident_id")
        meta["run_meta"] = run_meta

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
        target = dashboard_url(args.from_ts, args.to_ts)
        print("OPEN", target, flush=True)
        page.goto(target, wait_until="domcontentloaded", timeout=180000)
        page.wait_for_timeout(3000)
        print("URL", page.url[:160], flush=True)

        if not is_logged_in(page):
            if args.record_only:
                context.close()
                print("NOT_AUTHENTICATED", flush=True)
                return 2
            wait_for_login(page, args.login_timeout)
        else:
            print("SESSION_REUSED", page.url[:100], flush=True)

        record_sequence(page, meta, args)
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
