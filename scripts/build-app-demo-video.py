#!/usr/bin/env python3
"""
Build EdgeGuard Ops PRODUCT demo from real application footage.
- ONE voice: edge-tts vi-VN-NamMinhNeural only (no gTTS fallback).
- 85%+ real Datadog/terminal recordings; brief title/close overlays.
- Duration target 165–175s.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "docs" / "video"
REC = VIDEO / "recordings"
RAW = VIDEO / "raw-app"
PREVIEWS = VIDEO / "preview-frames"
EVIDENCE = ROOT / "docs" / "evidence" / "e2e-app-demo-20261019214254.json"
PERF = ROOT / "docs" / "evidence" / "performance-metrics.json"

VOICE = "vi-VN-NamMinhNeural"
RATE = "-10%"  # conversational, not rushed
W, H, FPS = 1920, 1080, 30

# Prefer clip with loaded widgets (dd-final-2); fall back if missing
DASH_CLIP = REC / "dd-final-2.mp4"
MONITOR_STILL = REC / "still-monitor.png"
DASH_STILL = REC / "still-dashboard.png"
TERM_CLIP = REC / "terminal-evidence-20261019215511.mp4"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"cmd failed {cmd[:4]}…\n{r.stderr[-1200:]}")
    return r


def wav_dur(p: Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def media_dur(p: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)])
    return float(r.stdout.strip())


def load_font(size: int, bold: bool = False):
    for c in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def make_title_card(path: Path, title: str, subtitle: str):
    img = Image.new("RGB", (W, H), (11, 18, 32))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([48, 36, 420, 78], 16, fill=(61, 220, 151))
    d.text((70, 44), "SIGNAL404", fill=(11, 18, 32), font=load_font(22, True))
    d.text((80, 420), title, fill=(232, 238, 247), font=load_font(64, True))
    d.text((80, 520), subtitle, fill=(139, 155, 176), font=load_font(28))
    d.text((80, 980), "SYNTHETIC TELEMETRY · real Datadog + MongoDB evidence", fill=(240, 192, 74), font=load_font(22, True))
    img.save(path)


def still_to_mp4(png: Path, seconds: float, out: Path, zoom: bool = True):
    """Slow pan/zoom over authentic UI still (labeled as captured UI frame)."""
    vf = f"scale={W}:{H}"
    if zoom:
        # mild zoom via zoompan
        frames = max(int(seconds * FPS), 1)
        vf = (
            f"scale=8000:-1,zoompan=z='min(zoom+0.0004,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}"
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(png),
                "-vf",
                vf,
                "-t",
                f"{seconds:.3f}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "fast",
                "-crf",
                "18",
                str(out),
            ]
        )
    else:
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(png),
                "-vf",
                f"scale={W}:{H}",
                "-t",
                f"{seconds:.3f}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(FPS),
                str(out),
            ]
        )


def trim_clip(src: Path, start: float, duration: float, out: Path):
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(src),
            "-t",
            f"{duration:.3f}",
            "-vf",
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "fast",
            "-crf",
            "18",
            str(out),
        ]
    )


def overlay_label(src: Path, out: Path, label: str):
    # drawtext at top — escape for Windows
    safe = label.replace(":", "\\:").replace("'", "")
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            (
                f"drawbox=x=40:y=24:w=iw-80:h=52:color=0x0B1220@0.75:t=fill,"
                f"drawtext=fontfile=/Windows/Fonts/segoeui.ttf:text='{safe}':"
                f"fontcolor=0xF0C04A:fontsize=22:x=56:y=36"
            ),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ]
    )


# Spoken script — pronunciation-friendly for NamMinh; one voice throughout.
# Keep ~165–175s at rate -10%.
NARRATION = """
Xin chào ban giám khảo. Em là thành viên đội Signal bốn không bốn.
Đây là Edge Guard Ops — demo trên ứng dụng thật: Đa-ta-đốc, terminal dịch vụ, và Mongo Đê Bê.

Trên màn hình là dashboard Edge Guard Fleet Operations.
Đây là giao diện Đa-ta-đốc đã đăng nhập, không phải slide PowerPoint.
Telemetry của thiết bị là synthetic, nhưng metrics, dashboard và monitor là quan sát thật.

Chúng em chạy vòng kín tự động: telemetry A P I, health analyzer và response worker khởi động trước.
Sau đó simulator inject kịch bản thermal throttle.

Khi nhiệt tăng, GPU vượt ngưỡng tám mươi lăm độ C.
Inference lai-ten-xi tăng rõ, ép-pi-ét giảm.
Dashboard ghi nhận spike GPU và latency, đồng thời có remediation action.

Analyzer mở incident thermal trên Mongo Đê Bê.
Worker đặt commanded profile bằng safe.
Simulator áp dụng và báo reported profile bằng safe.
Chúng em tách commanded và reported để không nhầm telemetry full với bằng chứng safe.

Incident đi qua MITIGATING, rồi RECOVERING.
Khi chuỗi mẫu healthy liên tục đủ cửa sổ quan sát, remediation VERIFIED và incident RESOLVED.

Trên terminal các bạn thấy log RESOLVED và VERIFIED,
cùng telemetry GPU khoảng năm mươi lăm độ, latency khoảng sáu mươi mili giây, ép-pi-ét khoảng mười tám.
Mười tám FPS là điểm vận hành safe mode — đổi peak FPS lấy headroom nhiệt.
Chúng em không claim khôi phục đủ khoảng ba mươi FPS.

Monitor Đa-ta-đốc sau recovery ở trạng thái O K.
Vì đây là run tự động với worker sẵn sàng, monitor có thể không giữ Alert lâu.
Demo staged — khởi động worker muộn để lộ Alert — là bằng chứng riêng đã công bố trước đây, không bị ghép giả thành một run liên tục.

Incident của run này: thermal edge không không một, ngày mười chín tháng mười năm hai không hai sáu.
Remediation action safe tương ứng đã VERIFIED.
Mongo Đê Bê là nguồn sự thật; Đa-ta-đốc là mặt quan sát cho vận hành.
Ây-pi-em live đã xác nhận trên telemetry A P I trong lần kiểm chứng trước.

Edge Guard Ops chứng minh Detect, Investigate, Respond, Verify trên dữ liệu giả lập có nhãn và quan sát thật.
Signal bốn không bốn. Cảm ơn ban giám khảo.
""".strip()


CAPTIONS = [
    ("Xin chào — EdgeGuard Ops · Signal404", 0.0, 8.0),
    ("Dashboard Datadog thật — không phải slide", 8.0, 22.0),
    ("Telemetry synthetic · quan sát Datadog thật", 22.0, 36.0),
    ("Automatic E2E — worker chạy sẵn trước fault", 36.0, 50.0),
    ("Thermal: GPU ↑ latency ↑ FPS ↓", 50.0, 68.0),
    ("commanded_profile=safe · reported_profile=safe", 68.0, 88.0),
    ("MITIGATING → RECOVERING → RESOLVED", 88.0, 108.0),
    ("Remediation VERIFIED trên MongoDB", 108.0, 125.0),
    ("Safe mode ≈ 18 FPS — không claim 30 FPS", 125.0, 142.0),
    ("Monitor OK · Alert staged là run riêng", 142.0, 158.0),
    ("Detect → Investigate → Respond → Verify", 158.0, 175.0),
]


async def synthesize_vo(out_mp3: Path, out_wav: Path):
    print("TTS edge-tts", VOICE, flush=True)
    communicate = edge_tts.Communicate(NARRATION, VOICE, rate=RATE)
    await communicate.save(str(out_mp3))
    if out_mp3.stat().st_size < 1000:
        raise RuntimeError("edge-tts returned empty audio — aborting (no gTTS fallback)")
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(out_mp3),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "1",
            str(out_wav),
        ]
    )


def write_srt(path: Path, total: float):
    def ts(sec: float) -> str:
        sec = max(0.0, min(sec, total))
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (text, t0, t1) in enumerate(CAPTIONS, 1):
        if t0 >= total:
            break
        t1 = min(t1, total)
        # wrap to 2 lines ~40 chars
        words = text.split()
        mid = max(1, len(words) // 2)
        body = " ".join(words[:mid]) + "\n" + " ".join(words[mid:]) if len(text) > 42 else text
        lines += [str(i), f"{ts(t0)} --> {ts(t1)}", body, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    if not DASH_CLIP.is_file():
        raise SystemExit(f"missing dashboard clip {DASH_CLIP}")
    if not TERM_CLIP.is_file():
        raise SystemExit(f"missing terminal clip {TERM_CLIP}")
    if not MONITOR_STILL.is_file() or not DASH_STILL.is_file():
        raise SystemExit("missing authentic Datadog stills")

    mp3 = VIDEO / "audio" / "app-demo-vo.mp3"
    wav = VIDEO / "voiceover-vi.wav"
    mp3.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_vo(mp3, wav))
    vo_len = wav_dur(wav)
    print(f"VO duration: {vo_len:.2f}s", flush=True)

    # Target video length = VO length (clamp 165–175 by adjusting visuals to VO)
    target = vo_len
    if target < 165 or target > 175:
        print(f"WARNING VO length {target:.1f} outside 165–175; edit narration if needed", flush=True)

    # Build visual segments totaling ~target
    title_png = RAW / "title.png"
    close_png = RAW / "close.png"
    make_title_card(title_png, "EdgeGuard Ops", "Closed-loop observability — live Datadog demo")
    make_title_card(close_png, "Signal404", "Detect → Investigate → Respond → Verify")

    segs = []
    # 0–5 title over still dashboard peek
    still_to_mp4(DASH_STILL, 5.0, RAW / "s00-titlebase.mp4", zoom=True)
    overlay_label(RAW / "s00-titlebase.mp4", RAW / "s00.mp4", "SYNTHETIC TELEMETRY · authentic Datadog UI capture")
    segs.append((RAW / "s00.mp4", 5.0))

    # Dashboard live clip — start after widgets load (~22s into clip)
    dash_dur = min(48.0, media_dur(DASH_CLIP) - 22.0)
    trim_clip(DASH_CLIP, 22.0, dash_dur, RAW / "s01-raw.mp4")
    overlay_label(RAW / "s01-raw.mp4", RAW / "s01.mp4", "Datadog · EdgeGuard Fleet Operations · live UI")
    segs.append((RAW / "s01.mp4", dash_dur))

    # Monitor still (authentic UI) — status OK after automatic recovery
    mon_dur = 18.0
    still_to_mp4(MONITOR_STILL, mon_dur, RAW / "s02-raw.mp4", zoom=True)
    overlay_label(
        RAW / "s02-raw.mp4",
        RAW / "s02.mp4",
        "Datadog monitor UI · status OK after automatic E2E recovery",
    )
    segs.append((RAW / "s02.mp4", mon_dur))

    # Terminal evidence
    term_use = min(38.0, media_dur(TERM_CLIP) - 1.0)
    trim_clip(TERM_CLIP, 1.0, term_use, RAW / "s03-raw.mp4")
    overlay_label(RAW / "s03-raw.mp4", RAW / "s03.mp4", "Terminal · RESOLVED / VERIFIED · reported_profile=safe")
    segs.append((RAW / "s03.mp4", term_use))

    # Dashboard still for metrics readability (same run graphs)
    metrics_dur = 22.0
    still_to_mp4(DASH_STILL, metrics_dur, RAW / "s04-raw.mp4", zoom=True)
    overlay_label(
        RAW / "s04-raw.mp4",
        RAW / "s04.mp4",
        "Captured Datadog dashboard frame · GPU/latency/FPS after safe profile",
    )
    segs.append((RAW / "s04.mp4", metrics_dur))

    # Close
    close_dur = 5.0
    still_to_mp4(close_png, close_dur, RAW / "s05.mp4", zoom=False)
    segs.append((RAW / "s05.mp4", close_dur))

    total_vis = sum(d for _, d in segs)
    print(f"Visual total {total_vis:.1f}s  VO {vo_len:.1f}s", flush=True)

    # If visuals longer than VO, trim last content segments; if shorter, extend metrics still
    if total_vis > vo_len + 0.5:
        # rebuild s04 shorter
        overflow = total_vis - vo_len
        new_m = max(8.0, metrics_dur - overflow)
        still_to_mp4(DASH_STILL, new_m, RAW / "s04-raw.mp4", zoom=True)
        overlay_label(
            RAW / "s04-raw.mp4",
            RAW / "s04.mp4",
            "Captured Datadog dashboard frame · GPU/latency/FPS after safe profile",
        )
        segs[4] = (RAW / "s04.mp4", new_m)
        total_vis = sum(d for _, d in segs)
    elif total_vis < vo_len - 0.5:
        need = vo_len - total_vis
        new_m = metrics_dur + need
        still_to_mp4(DASH_STILL, new_m, RAW / "s04-raw.mp4", zoom=True)
        overlay_label(
            RAW / "s04-raw.mp4",
            RAW / "s04.mp4",
            "Captured Datadog dashboard frame · GPU/latency/FPS after safe profile",
        )
        segs[4] = (RAW / "s04.mp4", new_m)
        total_vis = sum(d for _, d in segs)

    lst = RAW / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p, _ in segs), encoding="utf-8")
    silent = RAW / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    srt = VIDEO / "edgeguard-ops-subtitles.srt"
    write_srt(srt, min(total_vis, vo_len))

    final = VIDEO / "edgeguard-ops-final-demo.mp4"
    srt_esc = str(srt.resolve()).replace("\\", "/").replace(":", "\\:")
    style = (
        "FontName=Segoe UI,FontSize=16,PrimaryColour=&H00F0F4FA&,OutlineColour=&H90000000&,"
        "BackColour=&H90000000&,BorderStyle=4,Outline=0,Shadow=0,MarginV=44,Alignment=2"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(wav),
            "-vf",
            f"subtitles='{srt_esc}':force_style='{style}'",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{min(total_vis, vo_len):.3f}",
            "-movflags",
            "+faststart",
            str(final),
        ]
    )

    info = json.loads(
        run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(final)]
        ).stdout
    )
    duration = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")

    # QA frames
    for i, t in enumerate([3, 20, 45, 70, 95, 120, 145, max(duration - 3, 1)], 1):
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{t:.2f}",
                "-i",
                str(final),
                "-frames:v",
                "1",
                "-update",
                "1",
                str(PREVIEWS / f"app-qa-{i:02d}.png"),
            ]
        )

    incident = {}
    if EVIDENCE.is_file():
        incident = json.loads(EVIDENCE.read_text(encoding="utf-8-sig"))

    manifest = {
        "output": "docs/video/edgeguard-ops-final-demo.mp4",
        "kind": "real_application_demo",
        "duration_seconds": duration,
        "size_bytes": final.stat().st_size,
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "fps": 30,
        "tts_engine": "edge-tts",
        "tts_voice": VOICE,
        "tts_fallback_used": False,
        "voice_consistency": "single_engine_single_voice_entire_track",
        "footage_sources": {
            "datadog_dashboard_video": str(DASH_CLIP.relative_to(ROOT)).replace("\\", "/"),
            "datadog_dashboard_still": str(DASH_STILL.relative_to(ROOT)).replace("\\", "/"),
            "datadog_monitor_still": str(MONITOR_STILL.relative_to(ROOT)).replace("\\", "/"),
            "terminal_evidence": str(TERM_CLIP.relative_to(ROOT)).replace("\\", "/"),
        },
        "incident_run": {
            "id": "inc-thermal-edge-001-20261019144446",
            "mode": "automatic_e2e_workers_prestarted",
            "evidence": "docs/evidence/e2e-app-demo-20261019214254.json",
            "remediation": "act-safe-edge-001-20261019144450",
            "final": "RESOLVED / VERIFIED",
        },
        "disclosures": [
            "Telemetry is synthetic and labeled on-screen.",
            "This primary sequence is the automatic E2E run (workers pre-started).",
            "Monitor ALERT may be brief/absent vs staged-delay demo; monitor UI shows OK after recovery.",
            "Staged Alert demo (delayed worker) is a separate historical validation — not spliced as one continuous run.",
            "Safe-mode FPS ≈ 18 — not a claim of 30 FPS restoration.",
            "111.4s staged interval is NOT used as autonomous MTTA in this video.",
        ],
        "duration_ok": 165.0 <= duration <= 175.0,
        "slideshow_backup": "docs/video/edgeguard-ops-final-demo.slideshow-backup.mp4",
    }
    (VIDEO / "video-build-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("duration_seconds", "size_bytes", "duration_ok", "tts_voice", "tts_fallback_used")}, indent=2))
    return 0 if manifest["duration_ok"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print("BUILD_FAILED", e, file=sys.stderr)
        raise
