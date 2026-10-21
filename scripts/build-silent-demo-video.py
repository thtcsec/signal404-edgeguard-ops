#!/usr/bin/env python3
"""
Silent EdgeGuard demo: Inject Fault → Detect → Respond → Verify.
No TTS. No dashboard padding. Classic-conhost + loaded Datadog footage.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "docs" / "video"
REC = VIDEO / "recordings"
RAW = VIDEO / "raw-silent"
PREVIEWS = VIDEO / "preview-frames"
W, H, FPS = 1920, 1080, 30
DASH = REC / "dd-final-loaded.mp4"
SIM = REC / "conhost-sim-start.mp4"
MONGO = REC / "conhost-mongo-verify.mp4"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[:8]} failed\n{(r.stderr or '')[-1800:]}")
    return r


def dur(p: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)])
    return float(r.stdout.strip())


def font(size: int, bold: bool = False):
    for c in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def title_png(path: Path, title: str, sub: str):
    img = Image.new("RGB", (W, H), (11, 18, 32))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((48, 40, 280, 82), 14, fill=(61, 220, 151))
    d.text((68, 48), "SIGNAL404", fill=(11, 18, 32), font=font(20, True))
    d.text((80, 360), title, fill=(232, 238, 247), font=font(56, True))
    d.text((80, 450), sub, fill=(139, 155, 176), font=font(26))
    d.text((80, 560), "Inject Fault  →  Detect  →  Respond  →  Verify", fill=(240, 192, 74), font=font(28, True))
    d.text((80, 980), "SYNTHETIC TELEMETRY  ·  real Datadog + MongoDB  ·  E2E 20261021183352", fill=(139, 155, 176), font=font(18))
    img.save(path)


def still_mp4(png: Path, seconds: float, out: Path):
    run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(png),
            "-vf", f"scale={W}:{H}", "-t", f"{seconds:.2f}",
            "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            str(out),
        ]
    )


def clip(src: Path, start: float, length: float, out: Path, label: str, crop: str | None = None):
    safe = label.replace(":", "\\:").replace("'", "")
    parts = []
    if crop:
        parts.append(crop)
    parts.append(f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2")
    parts.append(f"fps={FPS}")
    parts.append("drawbox=x=0:y=0:w=iw:h=44:color=0x0B1220@0.78:t=fill")
    parts.append(
        f"drawtext=fontfile=/Windows/Fonts/segoeuib.ttf:text='{safe}':fontcolor=0xF0C04A:fontsize=20:x=18:y=10"
    )
    vf = ",".join(parts)
    run(
        [
            "ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", str(src), "-t", f"{length:.2f}",
            "-vf", vf, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            str(out),
        ]
    )


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    for p in (DASH, SIM, MONGO):
        if not p.is_file() or p.stat().st_size < 40_000:
            raise SystemExit(f"missing/unusable {p}")

    segs: list[Path] = []
    t = 0.0

    def add(path: Path, length: float):
        nonlocal t
        segs.append(path)
        t += length

    title_png(RAW / "title.png", "EdgeGuard Ops", "Automatic closed loop on synthetic edge cameras")
    still_mp4(RAW / "title.png", 3.0, RAW / "s00.mp4")
    add(RAW / "s00.mp4", 3.0)

    sim_len = min(18.0, dur(SIM) - 0.4)
    clip(SIM, 0.3, sim_len, RAW / "s01.mp4", "1  INJECT FAULT  ·  start THERMAL_THROTTLE  ·  same command as E2E 20261021183352")
    add(RAW / "s01.mp4", sim_len)

    # One loaded-dashboard pass (skip 0-8s spinners and 28-36s monitor white load).
    clip(DASH, 10.0, 16.0, RAW / "s02.mp4", "2  DETECT  ·  Datadog GPU / latency / incidents  ·  E2E 18:35 (not the 18:29 prior attempt)")
    add(RAW / "s02.mp4", 16.0)

    clip(
        DASH, 16.0, 10.0, RAW / "s03.mp4",
        "3  RESPOND  ·  Incident RESOLVED  inc-thermal-edge-001-20261021113510  ·  FPS 18 not 30",
        crop="crop=1600:300:160:430",
    )
    add(RAW / "s03.mp4", 10.0)

    mongo_len = min(22.0, dur(MONGO) - 0.4)
    clip(MONGO, 0.3, mongo_len, RAW / "s04.mp4", "4  VERIFY  ·  db.devices.findOne({_id:edge-001})  profile=safe  ·  worker RESOLVED")
    add(RAW / "s04.mp4", mongo_len)

    title_png(RAW / "close.png", "Signal404", "Inject Fault → Detect → Respond → Verify")
    still_mp4(RAW / "close.png", 3.0, RAW / "s05.mp4")
    add(RAW / "s05.mp4", 3.0)

    if t > 180:
        raise SystemExit(f"timeline too long {t:.1f}s")

    lst = RAW / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in segs), encoding="utf-8")
    silent = RAW / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    final = VIDEO / "edgeguard-ops-final-demo.mp4"
    run(
        [
            "ffmpeg", "-y", "-i", str(silent), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart",
            str(final),
        ]
    )

    info = json.loads(run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(final)]).stdout)
    duration = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")

    samples = [2, 8, 22, 38, 50, min(duration - 4, duration * 0.72), min(duration - 2, duration * 0.9)]
    for i, tsamp in enumerate(samples, 1):
        run(["ffmpeg", "-y", "-ss", f"{tsamp:.2f}", "-i", str(final), "-frames:v", "1", "-update", "1", str(PREVIEWS / f"silent-qa-{i:02d}.png")])

    manifest = {
        "output": "docs/video/edgeguard-ops-final-demo.mp4",
        "kind": "silent_real_application_demo",
        "e2e_run_id": "20261021183352",
        "incident_id": "inc-thermal-edge-001-20261021113510",
        "duration_seconds": duration,
        "size_bytes": final.stat().st_size,
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "audio_note": "silent AAC (anullsrc) — no TTS, no voiceover",
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "fps": 30,
        "tts_engine": None,
        "voiceover": False,
        "subtitles_burned_in": False,
        "duration_ok": 60.0 <= duration <= 180.0,
        "padded": False,
        "structure": ["Inject Fault", "Detect", "Respond", "Verify"],
        "sources": {
            "simulator_conhost": "docs/video/recordings/conhost-sim-start.mp4",
            "dashboard_video": "docs/video/recordings/dd-final-loaded.mp4",
            "mongo_conhost": "docs/video/recordings/conhost-mongo-verify.mp4",
        },
        "excluded_sources": [
            "desktop-e2e-*.mp4 (unrelated desktop apps)",
            "dd-live-loaded.mp4 (gdigrab captured foreground YouTube)",
            "terminal-evidence-mongo.mp4 (HTML dump, replaced by conhost)",
            "monitor Event Timeline 18:29 ALERT (prior same-day attempt, not E2E 18:35)",
        ],
        "recording_notes": [
            "OBS Studio is not installed on this machine.",
            "Windows Terminal title-grab records a black frame; classic conhost.exe GDI grab is used.",
            "Simulator recapture is a live start of THERMAL_THROTTLE; commanded profile is still safe from E2E so GPU stays ~54C. Datadog graphs are the 18:35 E2E, not this recapture.",
        ],
    }
    (VIDEO / "video-build-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("duration_seconds", "size_bytes", "duration_ok", "voiceover", "padded")}, indent=2))
    return 0 if manifest["duration_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
