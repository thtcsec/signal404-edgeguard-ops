#!/usr/bin/env python3
"""
Editorial EdgeGuard judge demo: Inject → Detect → Respond → Verify.
Silent (no TTS). Timeline-aligned SRT burned in. 16:9 fill, no 1600:300 crops.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "docs" / "video"
REC = VIDEO / "recordings"
RAW = VIDEO / "raw-editorial"
PREVIEWS = VIDEO / "preview-frames"
W, H, FPS = 1920, 1080, 30
SIM = REC / "conhost-sim-start.mp4"
WORKER = REC / "conhost-worker-respond.mp4"
MONGO = REC / "conhost-mongo-verify.mp4"
DASH_CANDIDATES = [
    REC / "dd-editorial.mp4",
    REC / "dd-final-loaded.mp4",
]
SRT = VIDEO / "edgeguard-ops-subtitles.srt"
FINAL = VIDEO / "edgeguard-ops-final-demo.mp4"
MANIFEST = VIDEO / "video-build-manifest.json"
QA_REPORT = ROOT / "docs" / "evidence" / "final-qa-editorial-20261021.md"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd[:10]} failed\n{(r.stderr or r.stdout or '')[-2200:]}")
    return r


def dur(p: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)])
    return float(r.stdout.strip())


def font(size: int, bold: bool = False):
    for c in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def load_run() -> dict:
    p = REC / "judge-e2e-run.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8-sig"))
    return {}


def find_dash() -> Path:
    webs = sorted((REC / "pw-video").glob("*.webm"), key=lambda x: x.stat().st_mtime, reverse=True)
    out = REC / "dd-editorial.mp4"
    if webs:
        newest = webs[0]
        if (not out.is_file()) or newest.stat().st_mtime > out.stat().st_mtime:
            run([
                "ffmpeg", "-y", "-i", str(newest),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
                "-an", str(out),
            ])
        return out
    for p in DASH_CANDIDATES:
        if p.is_file() and p.stat().st_size > 40_000:
            return p
    raise SystemExit("missing Datadog footage")


def parse_sim_cuts(log: Path) -> dict[str, float]:
    """Map simulator log lines to seconds from first telemetry sample."""
    if not log.is_file():
        return {}
    first: datetime | None = None
    gpu85: float | None = None
    safe: float | None = None
    iso_re = re.compile(r"^(\d{4}-\d{2}-\d{2}T[0-9:.+-]+)\s+edge-001\s+gpu=([0-9.]+)C.*?commanded_profile=(\w+)")
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = iso_re.search(line)
        if not m:
            continue
        ts = datetime.fromisoformat(m.group(1))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if first is None:
            first = ts
        rel = (ts - first).total_seconds()
        gpu = float(m.group(2))
        profile = m.group(3)
        if gpu85 is None and gpu >= 85.0:
            gpu85 = rel
        if safe is None and profile == "safe":
            safe = rel
    return {"gpu85": gpu85 or 22.0, "safe": safe or 45.0}


def title_png(path: Path, title: str, sub: str, run_id: str):
    img = Image.new("RGB", (W, H), (11, 18, 32))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((56, 48, 300, 96), 16, fill=(61, 220, 151))
    d.text((76, 58), "SIGNAL404", fill=(11, 18, 32), font=font(22, True))
    d.text((80, 300), title, fill=(232, 238, 247), font=font(64, True))
    d.text((80, 392), sub, fill=(139, 155, 176), font=font(28))
    d.text((80, 520), "Inject Fault   →   Detect   →   Respond   →   Verify", fill=(240, 192, 74), font=font(30, True))
    d.text((80, 620), "Automatic closed loop  ·  workers running before the fault", fill=(190, 202, 216), font=font(24))
    d.text((80, 980), f"SYNTHETIC TELEMETRY  ·  real Datadog + MongoDB  ·  E2E {run_id}", fill=(139, 155, 176), font=font(20))
    img.save(path)


def chip_png(path: Path, text: str):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((28, 24, 520, 72), 12, fill=(11, 18, 32, 210))
    d.text((46, 34), text, fill=(240, 192, 74), font=font(22, True))
    img.save(path)


def still_mp4(png: Path, seconds: float, out: Path):
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png),
        "-vf", f"scale={W}:{H}", "-t", f"{seconds:.2f}",
        "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(out),
    ])


def clip(
    src: Path,
    start: float,
    length: float,
    out: Path,
    chip: Path,
    zoom_console: bool = False,
    full_frame: bool = False,
    crop_y: int = 0,
):
    if zoom_console:
        # Zoom the text rows and leave a 120px well for burned-in captions.
        vf = f"crop={W}:760:0:{crop_y},scale={W}:960:flags=lanczos,pad={W}:{H}:0:0:color=0x0B1220,fps={FPS}"
    elif full_frame:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
    else:
        vf = (
            f"scale={W}:960:force_original_aspect_ratio=increase,"
            f"crop={W}:960,pad={W}:{H}:0:0:color=0x0B1220,fps={FPS}"
        )
    run([
        "ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", str(src), "-i", str(chip),
        "-t", f"{length:.2f}",
        "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(out),
    ])


def concat_list(paths: list[Path], out: Path):
    lst = RAW / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in paths), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])


def srt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def write_srt(cues: list[tuple[float, float, str]], path: Path):
    blocks = []
    for i, (a, b, text) in enumerate(cues, 1):
        blocks.append(f"{i}\n{srt_ts(a)} --> {srt_ts(b)}\n{text}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")


def burn_srt(src: Path, srt: Path, dst: Path):
    srt_esc = srt.resolve().as_posix().replace(":", "\\:")
    style = (
        "FontName=Segoe UI Semibold,FontSize=14,PrimaryColour=&H00F4F7FB,"
        "OutlineColour=&H00101828,BackColour=&HCC0B1220,BorderStyle=4,"
        "Outline=3,Shadow=0,MarginV=18,MarginL=60,MarginR=60,Alignment=2"
    )
    run([
        "ffmpeg", "-y", "-i", str(src), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", f"subtitles='{srt_esc}':force_style='{style}'",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart",
        str(dst),
    ])


def extract_frame(src: Path, t: float, dest: Path):
    run([
        "ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(src),
        "-frames:v", "1", "-update", "1", str(dest),
    ], check=False)


def freezedetect(src: Path) -> list[dict]:
    r = run([
        "ffmpeg", "-i", str(src),
        "-vf", "freezedetect=n=0.003:d=2.0",
        "-an", "-f", "null", "-",
    ], check=False)
    text = (r.stderr or "") + (r.stdout or "")
    events: list[dict] = []
    start = None
    for line in text.splitlines():
        if "freeze_start:" in line:
            try:
                start = float(line.split("freeze_start:")[-1].strip())
            except ValueError:
                start = None
        if "freeze_end:" in line and start is not None:
            try:
                rest = line.split("freeze_end:")[-1]
                end = float(rest.split()[0])
                dur_s = None
                if "freeze_duration:" in line:
                    dur_s = float(line.split("freeze_duration:")[-1].strip())
                events.append({"start": start, "end": end, "duration": dur_s or (end - start)})
            except ValueError:
                pass
            start = None
    return events


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    run_meta = load_run()
    run_id = str(run_meta.get("run_id") or "unknown")
    incident_id = str(run_meta.get("incident_id") or "")
    rem_id = str(run_meta.get("remediation_id") or "")

    dash = find_dash()
    for p in (SIM, WORKER, MONGO, dash):
        if not p.is_file() or p.stat().st_size < 40_000:
            raise SystemExit(f"missing/unusable {p}")

    sim_log = next(iter(sorted(REC.glob("term-sim-2026*.log"), reverse=True)), None)
    cuts = parse_sim_cuts(sim_log) if sim_log else {"gpu85": 22.0, "safe": 45.0}
    dash_dur = dur(dash)
    worker_dur = dur(WORKER)
    mongo_dur = dur(MONGO)

    segs: list[tuple[Path, float, str]] = []
    t = 0.0

    def add(path: Path, length: float, name: str):
        nonlocal t
        segs.append((path, length, name))
        t += length

    title_png(RAW / "title.png", "EdgeGuard Ops", "Judge demo — silent, authentic closed loop", run_id)
    still_mp4(RAW / "title.png", 3.2, RAW / "s00.mp4")
    add(RAW / "s00.mp4", 3.2, "title")

    chip_png(RAW / "chip-inject.png", "1  INJECT FAULT")
    # Live recording: start/climb from the header, then lower crop so newest safe-profile rows stay in frame.
    inject_a, inject_b = 44.0, 15.0
    clip(SIM, 0.5, inject_a, RAW / "s01a.mp4", RAW / "chip-inject.png", zoom_console=True, crop_y=0)
    clip(SIM, 44.5, inject_b, RAW / "s01b.mp4", RAW / "chip-inject.png", zoom_console=True, crop_y=250)
    concat_list([RAW / "s01a.mp4", RAW / "s01b.mp4"], RAW / "s01.mp4")
    add(RAW / "s01.mp4", inject_a + inject_b, "inject")

    chip_png(RAW / "chip-detect.png", "2  DETECT")
    dash_ss = 50.0
    dash_len = min(13.0, max(10.0, dash_dur - dash_ss - 0.4))
    clip(dash, dash_ss, dash_len, RAW / "s02.mp4", RAW / "chip-detect.png", full_frame=True)
    add(RAW / "s02.mp4", dash_len, "detect")

    chip_png(RAW / "chip-respond.png", "3  RESPOND")
    worker_ss = 1.8
    worker_len = min(7.8, max(7.0, worker_dur - worker_ss - 0.5))
    clip(WORKER, worker_ss, worker_len, RAW / "s03.mp4", RAW / "chip-respond.png", zoom_console=True)
    add(RAW / "s03.mp4", worker_len, "respond")

    chip_png(RAW / "chip-verify.png", "4  VERIFY")
    mongo_ss = 2.4
    mongo_len = min(3.9, max(3.6, mongo_dur - mongo_ss - 0.4))
    clip(MONGO, mongo_ss, mongo_len, RAW / "s04.mp4", RAW / "chip-verify.png", zoom_console=True)
    add(RAW / "s04.mp4", mongo_len, "verify")

    title_png(RAW / "close.png", "Signal404", "Inject Fault → Detect → Respond → Verify", run_id)
    still_mp4(RAW / "close.png", 3.2, RAW / "s05.mp4")
    add(RAW / "s05.mp4", 3.2, "close")

    if t > 180:
        raise SystemExit(f"timeline too long {t:.1f}s")

    timeline = []
    cursor = 0.0
    for path, length, name in segs:
        timeline.append({"name": name, "file": path.name, "start": round(cursor, 2), "end": round(cursor + length, 2)})
        cursor += length

    inject = next(x for x in timeline if x["name"] == "inject")
    detect = next(x for x in timeline if x["name"] == "detect")
    respond = next(x for x in timeline if x["name"] == "respond")
    verify = next(x for x in timeline if x["name"] == "verify")
    cues = [
        (0.0, inject["start"], "EdgeGuard Ops — automatic closed loop on synthetic edge cameras."),
        (inject["start"], inject["start"] + 12.0, "INJECT: start THERMAL_THROTTLE from a healthy full profile (~65°C, 29 FPS)."),
        (inject["start"] + 12.0, inject["start"] + 47.0, "GPU rises past 85°C and FPS drops. This is the injected thermal fault."),
        (inject["start"] + 47.0, inject["end"], "commanded_profile=safe is applied. Telemetry recovers to ~54°C / 18 FPS."),
        (detect["start"], detect["end"], f"DETECT: Datadog 3-minute window for E2E {run_id} only — synthetic telemetry."),
        (respond["start"], respond["start"] + 4.5, f"RESPOND: Remediation APPLIED — commanded_profile=safe. {rem_id}"),
        (respond["start"] + 4.5, respond["end"], f"Incident RESOLVED after healthy safe-profile telemetry. {incident_id}"),
        (verify["start"], verify["end"], "VERIFY: MongoDB status=RESOLVED, action=VERIFIED, device.profile=safe."),
        (verify["end"], cursor, "Inject Fault → Detect → Respond → Verify"),
    ]

    write_srt(cues, SRT)

    concat_list([p for p, _, _ in segs], RAW / "silent.mp4")
    burn_srt(RAW / "silent.mp4", SRT, FINAL)

    info = json.loads(run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(FINAL)]).stdout)
    duration = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})

    qa_times = []
    t0 = 0.0
    while t0 < duration - 0.05:
        qa_times.append(("tick", t0))
        t0 += 5.0
    for sc in timeline:
        qa_times.append(("scene", sc["start"] + 0.15))
    qa_times.append(("end", max(0.0, duration - 0.4)))

    seen = set()
    qa_files = []
    n = 0
    for kind, tsamp in qa_times:
        key = round(tsamp, 1)
        if key in seen:
            continue
        seen.add(key)
        n += 1
        dest = PREVIEWS / f"editorial-qa-{n:02d}.png"
        extract_frame(FINAL, min(tsamp, duration - 0.15), dest)
        qa_files.append({"n": n, "t": round(tsamp, 2), "kind": kind, "file": dest.name})
        if dest.is_file():
            img = Image.open(dest)
            img.resize((854, 480)).save(PREVIEWS / f"editorial-qa-{n:02d}-mobile.png")

    freezes = freezedetect(FINAL)
    long_freezes = [f for f in freezes if f["duration"] > 4.0]
    justified = []
    for f in long_freezes:
        mid = (f["start"] + f["end"]) / 2
        name = next((s["name"] for s in timeline if s["start"] <= mid <= s["end"]), "")
        if name in {"title", "close"}:
            justified.append({**f, "justification": f"{name} card ({f['duration']:.1f}s)"})
        elif name == "inject":
            justified.append({**f, "justification": "live console: telemetry lines update on a black field (few pixels change)"})
        elif name == "detect":
            justified.append({**f, "justification": "paused Datadog 3-minute window — graphs are historical, not live-ticking"})
        elif name == "respond":
            justified.append({**f, "justification": "UNJUSTIFIED — trim idle after APPLIED/RESOLVED lines"})
        elif name == "verify":
            justified.append({**f, "justification": "short mongosh hold so incident/action/device fields are readable"})
        else:
            justified.append({**f, "justification": "UNJUSTIFIED — inspect/trim"})

    duration_ok = 90.0 <= duration <= 180.0
    target_ok = 90.0 <= duration <= 105.0
    captions_ok = True  # visual inspection fills this in the QA report

    manifest = {
        "output": "docs/video/edgeguard-ops-final-demo.mp4",
        "kind": "silent_editorial_judge_demo",
        "e2e_run_id": run_id,
        "incident_id": incident_id,
        "remediation_id": rem_id,
        "duration_seconds": duration,
        "size_bytes": FINAL.stat().st_size,
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "audio_note": "silent AAC (anullsrc) — no TTS, no voiceover",
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "fps": 30,
        "tts_engine": None,
        "voiceover": False,
        "subtitles_burned_in": True,
        "subtitles_file": "docs/video/edgeguard-ops-subtitles.srt",
        "duration_ok": duration_ok,
        "duration_target_ok": target_ok,
        "padded": False,
        "structure": ["Inject Fault", "Detect", "Respond", "Verify"],
        "timeline": timeline,
        "sim_cuts": cuts,
        "sources": {
            "simulator_conhost": "docs/video/recordings/conhost-sim-start.mp4",
            "dashboard_video": str(dash.relative_to(ROOT)).replace("\\", "/"),
            "worker_conhost": "docs/video/recordings/conhost-worker-respond.mp4",
            "mongo_conhost": "docs/video/recordings/conhost-mongo-verify.mp4",
        },
        "freezedetect": freezes,
        "long_freezes": justified,
        "qa_frames": qa_files,
        "recording_notes": [
            "OBS Studio is not installed; classic conhost.exe + ffmpeg gdigrab is used.",
            "Windows Terminal title-grab records a black frame and is not used.",
            "Datadog captured with an explicit from_ts/to_ts window for this E2E; graph hover disabled.",
            "Respond uses a 16:9 conhost of this run's worker log (APPLIED before RESOLVED), not a 1600:300 crop.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "duration_seconds": duration,
        "duration_ok": duration_ok,
        "duration_target_ok": target_ok,
        "subtitles_burned_in": True,
        "long_freezes": justified,
        "run_id": run_id,
        "incident_id": incident_id,
    }, indent=2))
    return 0 if duration_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
