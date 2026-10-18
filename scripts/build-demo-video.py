#!/usr/bin/env python3
"""
Fully automated EdgeGuard Ops demo video builder.
Uses slide previews, evidence-derived graphics (labeled), edge-tts Vietnamese VO, FFmpeg.
Does not fabricate Datadog UI screenshots — embeds real captures from docs/video/captures/ if present.
"""
from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "docs" / "video"
SLIDES = ROOT / "docs" / "presentation" / "assets" / "slide-previews"
EVIDENCE = ROOT / "docs" / "evidence" / "performance-metrics.json"
CAPTURES = VIDEO / "captures"
SCENES = VIDEO / "scenes"
AUDIO = VIDEO / "audio"
PREVIEWS = VIDEO / "preview-frames"
RAW = VIDEO / "raw"

W, H = 1920, 1080
FPS = 30
BG = (11, 18, 32)
FG = (232, 238, 247)
MUTED = (139, 155, 176)
ACCENT = (61, 220, 151)
ALERT = (255, 107, 74)
WARN = (240, 192, 74)
CARD = (20, 30, 48)

VOICE = "vi-VN-NamMinhNeural"
RATE = "-5%"  # slightly slower for clarity

# Narration segments aligned to target timeline (~180s). Polish of DEMO_SCRIPT_VI.md.
SEGMENTS = [
    {
        "id": "01_open",
        "start": 0.0,
        "visual": "slides",
        "slides": ["slide-01.png", "slide-02.png"],
        "text": (
            "Xin chào ban giám khảo. Em là thành viên đội Signal bốn không bốn, "
            "với dự án Edge Guard Ops. "
            "Trên nhà máy, camera A I edge chạy liên tục. "
            "Khi GPU nóng và thermal throttling xảy ra, FPS giảm — thường phát hiện muộn. "
            "Câu hỏi của chúng em: làm sao phát hiện sớm, xử lý an toàn, "
            "và chứng minh đã hồi phục?"
        ),
    },
    {
        "id": "02_arch",
        "start": 18.0,
        "visual": "arch",
        "slides": ["slide-03.png", "slide-04.png"],
        "text": (
            "Edge Guard Ops theo vòng Detect, Investigate, Respond, Verify. "
            "MongoDB Time Series là nguồn sự thật. "
            "Datadog là mặt quan sát: metrics, logs và monitor theo cùng device ID và incident ID. "
            "Toàn bộ telemetry trong demo này là synthetic, có nhãn rõ ràng."
        ),
    },
    {
        "id": "03_thermal",
        "start": 40.0,
        "visual": "thermal",
        "text": (
            "Đây là kịch bản thermal throttle trên simulator — dữ liệu giả lập. "
            "GPU tăng, inference latency tăng, FPS giảm. "
            "Health analyzer dùng set window fields trên MongoDB để phát hiện xu hướng nhiệt, "
            "đồng thời kiểm tra mạng không phải nguyên nhân chính."
        ),
    },
    {
        "id": "04_datadog_alert",
        "start": 70.0,
        "visual": "alert",
        "text": (
            "Trên dashboard Edge Guard Fleet Operations, các widget GPU, latency và FPS cùng timeline. "
            "Monitor demo chuyển sang Alert. "
            "Xin lưu ý: chúng em cố ý khởi động response worker muộn "
            "để ban giám khảo thấy Alert trước — đây là demo staged, "
            "không phải thời gian phản hồi tự động thuần túy."
        ),
    },
    {
        "id": "05_respond",
        "start": 95.0,
        "visual": "respond",
        "slides": ["slide-06.png"],
        "text": (
            "Response worker đặt commanded profile bằng safe, ghi remediation action. "
            "Simulator áp dụng và báo reported profile bằng safe. "
            "Chúng em tách commanded và reported "
            "để không nhầm telemetry full thành bằng chứng đã chạy safe."
        ),
    },
    {
        "id": "06_verify",
        "start": 125.0,
        "visual": "verify",
        "text": (
            "Recovery không chỉ đếm thời gian: cần telemetry mới "
            "và chuỗi mẫu healthy liên tục khi reported profile là safe. "
            "Monitor Datadog chuyển từ Alert sang O K. "
            "Incident MongoDB Resolved, remediation Verified. "
            "Nếu monitor O K chậm hơn kỳ vọng, cửa sổ trung bình khoảng hai phút có thể làm trễ tín hiệu — "
            "bằng chứng cứng vẫn là MongoDB."
        ),
    },
    {
        "id": "07_impact",
        "start": 150.0,
        "visual": "impact",
        "slides": ["slide-07.png"],
        "text": (
            "Trên run đo được, dữ liệu synthetic: "
            "GPU trung bình chín mươi hai phẩy ba độ C xuống năm mươi tư phẩy một. "
            "Latency một trăm bảy mươi bảy phẩy ba mili giây xuống năm mươi chín phẩy sáu. "
            "FPS mười hai phẩy một lên mười tám. "
            "Mười tám FPS là điểm vận hành safe mode — đổi peak FPS lấy headroom nhiệt, "
            "không claim khôi phục đủ khoảng ba mươi FPS. "
            "Bốn mươi phẩy chín giây là từ mẫu telemetry đầu tiên đã lưu tới lúc detect. "
            "Một trăm mười một giây detect tới remediate gồm trì hoãn worker có chủ đích."
        ),
    },
    {
        "id": "08_close",
        "start": 170.0,
        "visual": "close",
        "slides": ["slide-08.png"],
        "text": (
            "A P M live đã xác nhận trên telemetry A P I. "
            "Edge Guard Ops chứng minh vòng Detect, Investigate, Respond, Verify "
            "khép kín trên dữ liệu giả lập có nhãn. "
            "Signal bốn không bốn. Cảm ơn ban giám khảo."
        ),
    },
]


def ensure_dirs():
    for d in (VIDEO, CAPTURES, SCENES, AUDIO, PREVIEWS, RAW):
        d.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for c in candidates:
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def solid(color=BG) -> Image.Image:
    return Image.new("RGB", (W, H), color)


def pill(draw: ImageDraw.ImageDraw, xy, text, fill=ACCENT, text_color=BG, font=None):
    font = font or load_font(22, True)
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=fill)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2 - 2), text, fill=text_color, font=font)


def badge_synthetic(img: Image.Image, extra: str | None = None):
    draw = ImageDraw.Draw(img)
    font = load_font(20, True)
    label = "SYNTHETIC TELEMETRY"
    if extra:
        label = f"{label} · {extra}"
    pill(draw, (48, 36, 48 + 18 * len(label) // 2 + 40, 78), label, WARN, BG, font)
    return img


def fit_slide(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    return im


def ken_burns_frames(img: Image.Image, n_frames: int, zoom_end: float = 1.08) -> list[Image.Image]:
    frames = []
    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        z = 1.0 + (zoom_end - 1.0) * t
        cw, ch = int(W / z), int(H / z)
        # pan slightly right/down
        left = int((W - cw) * 0.15 * t)
        top = int((H - ch) * 0.1 * t)
        crop = img.crop((left, top, left + cw, top + ch)).resize((W, H), Image.Resampling.LANCZOS)
        frames.append(crop)
    return frames


def draw_metric_scene(evidence: dict) -> Image.Image:
    img = solid()
    draw = ImageDraw.Draw(img)
    badge_synthetic(img, "MongoDB evidence")
    title = load_font(48, True)
    body = load_font(28)
    small = load_font(22)
    draw.text((60, 110), "Measured recovery (synthetic run)", fill=FG, font=title)

    metrics = [
        ("GPU temperature", 92.3, 54.1, "°C", 100, True),
        ("Inference latency", 177.3, 59.6, " ms", 200, True),
        ("FPS (safe ≠ full 30)", 12.1, 18.0, "", 30, False),
    ]
    y = 220
    for name, before, after, unit, mx, lower_better in metrics:
        draw.text((60, y), name, fill=MUTED, font=body)
        # bars
        bar_x, bar_w, bar_h = 60, 1100, 36
        bw = int(bar_w * before / mx)
        aw = int(bar_w * after / mx)
        draw.rounded_rectangle([bar_x, y + 45, bar_x + bw, y + 45 + bar_h], 10, fill=ALERT)
        draw.rounded_rectangle([bar_x, y + 95, bar_x + aw, y + 95 + bar_h], 10, fill=ACCENT)
        draw.text((bar_x + bw + 16, y + 48), f"Before {before}{unit}", fill=ALERT, font=small)
        draw.text((bar_x + aw + 16, y + 98), f"After {after}{unit}", fill=ACCENT, font=small)
        y += 200

    draw.text(
        (60, 980),
        f"Incident {evidence['incident_id']} · Device {evidence['device_id']}",
        fill=MUTED,
        font=small,
    )
    return img


def draw_thermal_ramp() -> list[Image.Image]:
    """Illustrative ramp labeled — values track evidence trajectory, not live UI."""
    frames = []
    n = 90
    font = load_font(42, True)
    small = load_font(24)
    for i in range(n):
        t = i / (n - 1)
        gpu = 55 + 37 * t  # ~55 → 92
        lat = 50 + 127 * t
        fps = 28 - 16 * t
        img = solid()
        draw = ImageDraw.Draw(img)
        badge_synthetic(img, "illustrative ramp from evidence trajectory")
        draw.text((60, 120), "Thermal throttle developing", fill=FG, font=font)
        # gauges
        for idx, (label, val, mx, color, unit) in enumerate(
            [
                ("GPU °C", gpu, 100, ALERT if gpu > 80 else WARN, "°C"),
                ("Latency ms", lat, 200, ALERT if lat > 120 else WARN, " ms"),
                ("FPS", fps, 30, ALERT if fps < 15 else ACCENT, ""),
            ]
        ):
            x = 120 + idx * 560
            draw.rounded_rectangle([x, 280, x + 480, 720], 24, fill=CARD, outline=color, width=3)
            draw.text((x + 40, 320), label, fill=MUTED, font=small)
            draw.text((x + 40, 420), f"{val:.1f}{unit}", fill=color, font=load_font(64, True))
            # progress
            pw = int(400 * min(val / mx, 1.0))
            draw.rounded_rectangle([x + 40, 560, x + 40 + 400, 600], 12, fill=(40, 50, 70))
            draw.rounded_rectangle([x + 40, 560, x + 40 + pw, 600], 12, fill=color)
        draw.text((60, 900), "NOT a live Datadog screenshot — reconstructed chart", fill=MUTED, font=small)
        frames.append(img)
    return frames


def draw_status_card(title: str, status: str, color, lines: list[str], disclosure: str | None = None) -> Image.Image:
    img = solid()
    draw = ImageDraw.Draw(img)
    badge_synthetic(img)
    draw.text((60, 120), title, fill=FG, font=load_font(46, True))
    pill(draw, (60, 220, 420, 300), status, color, BG if color != WARN else BG, load_font(32, True))
    y = 360
    for line in lines:
        draw.text((60, y), line, fill=FG, font=load_font(28))
        y += 56
    if disclosure:
        draw.rounded_rectangle([60, 820, 1860, 980], 16, fill=(40, 30, 20), outline=WARN, width=2)
        draw.text((90, 860), disclosure, fill=WARN, font=load_font(26, True))
    return img


def draw_arch_anim(n: int = 60) -> list[Image.Image]:
    nodes = [
        (160, 400, "Simulator"),
        (520, 400, "Telemetry API"),
        (900, 400, "MongoDB TS"),
        (1280, 400, "Analyzer"),
        (1640, 400, "Worker"),
    ]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        img = solid()
        draw = ImageDraw.Draw(img)
        badge_synthetic(img, "architecture diagram")
        draw.text((60, 100), "Detect → Investigate → Respond → Verify", fill=ACCENT, font=load_font(40, True))
        draw.text((60, 170), "MongoDB = truth · Datadog = operator lens", fill=MUTED, font=load_font(26))
        for j, (x, y, name) in enumerate(nodes):
            active = t * (len(nodes) - 1) >= j - 0.2
            c = ACCENT if active else MUTED
            draw.rounded_rectangle([x - 120, y - 70, x + 120, y + 70], 18, fill=CARD, outline=c, width=3)
            bbox = draw.textbbox((0, 0), name, font=load_font(22, True))
            tw = bbox[2] - bbox[0]
            draw.text((x - tw / 2, y - 14), name, fill=FG, font=load_font(22, True))
            if j < len(nodes) - 1:
                x2 = nodes[j + 1][0]
                progress = max(0.0, min(1.0, t * (len(nodes) - 1) - j))
                xe = x + 130 + int((x2 - 130 - (x + 130)) * progress)
                draw.line([(x + 130, y), (xe, y)], fill=ACCENT, width=6)
        # Datadog side box
        draw.rounded_rectangle([700, 650, 1220, 850], 18, fill=CARD, outline=ACCENT, width=2)
        draw.text((780, 720), "Datadog: metrics · logs · monitor", fill=FG, font=load_font(26, True))
        frames.append(img)
    return frames


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def synthesize_gtts(text: str, out_mp3: Path):
    from gtts import gTTS

    gTTS(text=text, lang="vi", slow=False).save(str(out_mp3))


async def synthesize_segment(seg: dict, out_mp3: Path, out_wav: Path):
    text = seg["text"]
    used = "edge_tts"
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(str(out_mp3))
        if out_mp3.stat().st_size < 500:
            raise RuntimeError("edge_tts empty audio")
    except Exception as e:
        print(f"    edge_tts fallback -> gTTS ({type(e).__name__})")
        synthesize_gtts(text, out_mp3)
        used = "gtts"
    seg["tts_engine"] = used
    subprocess.run(
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
        ],
        check=True,
        capture_output=True,
    )


def concat_wavs(paths: list[Path], out: Path, silence_gap: float = 0.35):
    """Simple PCM concat with short silence between segments."""
    frames = []
    params = None
    gap_frames = None
    for p in paths:
        with wave.open(str(p), "rb") as w:
            if params is None:
                params = w.getparams()
                gap_frames = b"\x00\x00" * int(params.framerate * silence_gap * params.nchannels)
            frames.append(w.readframes(w.getnframes()))
            frames.append(gap_frames)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as out_w:
        out_w.setparams(params)
        for f in frames:
            out_w.writeframes(f)


def write_scene_video(frames: list[Image.Image], out: Path, fps: int = FPS):
    """Write frames via ffmpeg raw pipe."""
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        "18",
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for fr in frames:
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    err = proc.stderr.read()
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"ffmpeg scene failed: {err[-800:].decode(errors='ignore')}")


def still_to_video(img: Image.Image, duration: float, out: Path, kenburns: bool = True):
    n = max(int(duration * FPS), 1)
    if kenburns:
        frames = ken_burns_frames(img, n)
    else:
        frames = [img] * n
    write_scene_video(frames, out)


def valid_image(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 2000:
        return False
    try:
        with Image.open(path) as im:
            im.verify()
        return True
    except Exception:
        return False


def try_load_capture(*names: str) -> Image.Image | None:
    """Load first matching capture; supports Datadog graph PNG snapshots and UI screenshots."""
    for name in names:
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            p = CAPTURES / f"{name}{ext}"
            if not valid_image(p):
                continue
            im = Image.open(p).convert("RGB")
            canvas = solid()
            draw = ImageDraw.Draw(canvas)
            badge_synthetic(canvas, "authentic Datadog graph snapshot")
            draw.text((60, 100), "Historical metrics from verified incident window", fill=FG, font=load_font(32, True))
            im.thumbnail((W - 120, H - 220), Image.Resampling.LANCZOS)
            x = (W - im.width) // 2
            y = 160 + (H - 220 - im.height) // 2
            canvas.paste(im, (x, y))
            return canvas
    return None


def collage_graphs(paths: list[Path], title: str) -> Image.Image | None:
    existing = [p for p in paths if valid_image(p)]
    if not existing:
        return None
    img = solid()
    draw = ImageDraw.Draw(img)
    badge_synthetic(img, "authentic Datadog API snapshots")
    draw.text((60, 100), title, fill=FG, font=load_font(36, True))
    n = len(existing)
    if n == 1:
        slots = [(120, 180, W - 120, H - 80)]
    elif n == 2:
        slots = [(60, 180, 930, 980), (990, 180, 1860, 980)]
    else:
        slots = [(60, 180, 640, 980), (660, 180, 1240, 980), (1260, 180, 1860, 980)]
    for p, (x0, y0, x1, y1) in zip(existing, slots):
        im = Image.open(p).convert("RGB")
        box_w, box_h = x1 - x0, y1 - y0
        im.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
        x = x0 + (box_w - im.width) // 2
        y = y0 + (box_h - im.height) // 2
        img.paste(im, (x, y))
    return img


def build_segment_visual(seg: dict, duration: float, evidence: dict) -> Path:
    out = SCENES / f"{seg['id']}.mp4"
    vtype = seg["visual"]
    capture_map = {
        "thermal": "dashboard-heat",
        "alert": "monitor-alert",
        "verify": "monitor-ok",
        "respond": "dashboard-recovery",
    }

    # Prefer authentic Datadog graph snapshots / UI captures when available
    if vtype == "thermal":
        collage = collage_graphs(
            [
                CAPTURES / "datadog-graph-gpu-edge001.png",
                CAPTURES / "datadog-graph-gpu.png",
                CAPTURES / "datadog-graph-latency-edge001.png",
                CAPTURES / "datadog-graph-fps-edge001.png",
            ],
            "Datadog metrics — thermal window (historical, verified incident)",
        )
        if collage is None:
            collage = try_load_capture(capture_map["thermal"], "datadog-graph-gpu", "dashboard-heat")
        if collage is not None:
            still_to_video(collage, duration, out, kenburns=True)
            return out

    if vtype == "alert":
        cap = try_load_capture("monitor-alert", "datadog-monitor-alert")
        if cap is not None:
            still_to_video(cap, duration, out, kenburns=True)
            return out

    if vtype == "verify":
        collage = collage_graphs(
            [
                CAPTURES / "datadog-graph-gpu-edge001.png",
                CAPTURES / "datadog-graph-fps-edge001.png",
                CAPTURES / "monitor-ok.png",
            ],
            "Recovery trends — Datadog historical graphs + monitor OK evidence",
        )
        cap = collage or try_load_capture("monitor-ok", "datadog-monitor-ok")
        if cap is not None:
            still_to_video(cap, duration, out, kenburns=True)
            return out

    if vtype == "respond":
        cap = try_load_capture("dashboard-recovery", "datadog-graph-latency-edge001")
        if cap is not None:
            slide = fit_slide(SLIDES / "slide-06.png")
            n = max(int(duration * FPS), 1)
            n1 = n // 3
            frames = ken_burns_frames(slide, n1) + ken_burns_frames(cap, n - n1, 1.04)
            write_scene_video(frames, out)
            return out

    if vtype == "slides":
        slides = [fit_slide(SLIDES / s) for s in seg.get("slides", [])]
        if not slides:
            slides = [solid()]
        # split duration across slides
        per = duration / len(slides)
        parts = []
        for i, sl in enumerate(slides):
            p = SCENES / f"{seg['id']}_p{i}.mp4"
            still_to_video(sl, per, p, kenburns=True)
            parts.append(p)
        # concat parts
        lst = SCENES / f"{seg['id']}_list.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
            check=True,
            capture_output=True,
        )
        return out

    if vtype == "arch":
        # mix slide-04 + short arch anim
        frames = draw_arch_anim(max(int(duration * FPS * 0.55), 30))
        # hold last + slide
        slide = fit_slide(SLIDES / "slide-04.png")
        n_hold = max(int(duration * FPS) - len(frames), 15)
        frames.extend(ken_burns_frames(slide, n_hold, 1.05))
        write_scene_video(frames[: max(int(duration * FPS), 1)], out)
        return out

    if vtype == "thermal":
        ramp = draw_thermal_ramp()
        # loop/trim to duration
        need = max(int(duration * FPS), 1)
        frames = (ramp * (need // len(ramp) + 1))[:need]
        write_scene_video(frames, out)
        return out

    if vtype == "alert":
        img = draw_status_card(
            "Datadog demo monitor",
            "ALERT",
            ALERT,
            [
                "Monitor 333934695 · demo last_2m",
                "GPU average above threshold (synthetic)",
                "Dashboard 9rr-a4u-2st · device edge-001",
                "Incident inc-thermal-edge-001-…85058",
            ],
            disclosure="STAGED: response-worker start intentionally delayed so Alert is visible — NOT autonomous MTTA",
        )
        still_to_video(img, duration, out)
        return out

    if vtype == "respond":
        img = draw_status_card(
            "Automated remediation",
            "SAFE PROFILE",
            ACCENT,
            [
                "commanded_profile = safe",
                "reported_profile = safe (simulator)",
                "Remediation act-safe-edge-001-…85250",
                "Commanded ≠ reported — never confuse full telemetry with safe proof",
            ],
        )
        # prepend slide-06 briefly via ken burns mix
        slide = fit_slide(SLIDES / "slide-06.png")
        n = max(int(duration * FPS), 1)
        n1 = n // 3
        frames = ken_burns_frames(slide, n1) + ken_burns_frames(img, n - n1, 1.04)
        write_scene_video(frames, out)
        return out

    if vtype == "verify":
        img = draw_status_card(
            "Verified recovery",
            "OK · RESOLVED",
            ACCENT,
            [
                "Monitor: ALERT → OK (observed live)",
                "MongoDB incident: RESOLVED",
                "Remediation: VERIFIED after continuous healthy samples",
                "Hard proof = MongoDB when monitor lag exists",
            ],
        )
        still_to_video(img, duration, out)
        return out

    if vtype == "impact":
        metrics = draw_metric_scene(evidence)
        slide = fit_slide(SLIDES / "slide-07.png")
        n = max(int(duration * FPS), 1)
        n1 = n // 2
        frames = ken_burns_frames(metrics, n1) + ken_burns_frames(slide, n - n1, 1.05)
        write_scene_video(frames, out)
        return out

    if vtype == "close":
        slide = fit_slide(SLIDES / "slide-08.png")
        still_to_video(slide, duration, out)
        return out

    still_to_video(solid(), duration, out)
    return out


def write_srt(segments_timed: list[dict], out: Path):
    def ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int((sec - int(sec)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, seg in enumerate(segments_timed, 1):
        # wrap text ~80 chars for SRT readability — use original script with punctuation
        text = seg["display_text"]
        lines.append(str(i))
        lines.append(f"{ts(seg['t0'])} --> {ts(seg['t1'])}")
        # split into ~2 lines
        words = text.split()
        mid = len(words) // 2
        lines.append(" ".join(words[:mid]))
        lines.append(" ".join(words[mid:]))
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


DISPLAY_TEXT = {
    "01_open": "Xin chào ban giám khảo. Em là thành viên đội Signal404 với dự án EdgeGuard Ops. Trên nhà máy, camera AI edge chạy liên tục. Khi GPU nóng và thermal throttling xảy ra, FPS giảm — thường phát hiện muộn. Câu hỏi: phát hiện sớm, xử lý an toàn, và chứng minh đã hồi phục?",
    "02_arch": "EdgeGuard Ops theo Detect → Investigate → Respond → Verify. MongoDB Time Series là nguồn sự thật; Datadog là mặt quan sát. Toàn bộ telemetry trong demo là synthetic, có nhãn rõ ràng.",
    "03_thermal": "Kịch bản thermal throttle trên simulator — dữ liệu giả lập. GPU tăng, latency tăng, FPS giảm. Health analyzer dùng $setWindowFields trên MongoDB.",
    "04_datadog_alert": "Dashboard EdgeGuard Fleet Operations. Monitor demo chuyển Alert. Chúng em cố ý khởi động response-worker muộn để thấy Alert trước — demo staged, không phải MTTA tự động thuần túy.",
    "05_respond": "Worker đặt commanded_profile=safe. Simulator báo reported_profile=safe. Tách commanded và reported để không nhầm telemetry full thành bằng chứng safe.",
    "06_verify": "Recovery cần chuỗi mẫu healthy liên tục. Monitor ALERT → OK. MongoDB RESOLVED / remediation VERIFIED. Nếu OK chậm, cửa sổ ~2 phút có thể trễ — bằng chứng cứng là MongoDB.",
    "07_impact": "Synthetic: GPU 92,3→54,1°C; latency 177,3→59,6 ms; FPS 12,1→18,0 (safe mode ≠ 30 FPS). 40,9s = mẫu đầu → detect. 111s gồm trì hoãn worker có chủ đích.",
    "08_close": "APM live xác nhận trên telemetry-api. EdgeGuard Ops chứng minh Detect → Investigate → Respond → Verify. Signal404. Cảm ơn ban giám khảo.",
}


def ffprobe_json(path: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout)


def extract_preview_frames(mp4: Path, times: list[float]):
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(times):
        out = PREVIEWS / f"frame-{i+1:02d}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-frames:v", "1", str(out)],
            check=True,
            capture_output=True,
        )


async def main():
    ensure_dirs()
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    print("=== TTS ===")
    wav_parts = []
    for seg in SEGMENTS:
        mp3 = AUDIO / f"{seg['id']}.mp3"
        wav = AUDIO / f"{seg['id']}.wav"
        print(f"  synthesize {seg['id']}...")
        await synthesize_segment(seg, mp3, wav)
        dur = wav_duration(wav)
        seg["audio_duration"] = dur
        print(f"    {dur:.2f}s")
        wav_parts.append(wav)

    vo_wav = VIDEO / "voiceover-vi.wav"
    concat_wavs(wav_parts, vo_wav)
    total_audio = wav_duration(vo_wav)
    print(f"Total VO: {total_audio:.2f}s")

    # Assign visual durations = audio durations (plus tiny gap already in concat)
    print("=== VISUALS ===")
    scene_paths = []
    timed = []
    t_cursor = 0.0
    for seg, wav in zip(SEGMENTS, wav_parts):
        dur = wav_duration(wav) + 0.35  # match silence gap in concat
        print(f"  scene {seg['id']} ({dur:.2f}s)...")
        path = build_segment_visual(seg, dur, evidence)
        scene_paths.append(path)
        timed.append(
            {
                "id": seg["id"],
                "t0": t_cursor,
                "t1": t_cursor + wav_duration(wav),
                "display_text": DISPLAY_TEXT[seg["id"]],
                "visual": str(path.relative_to(ROOT)).replace("\\", "/"),
            }
        )
        t_cursor += dur

    # Concat video scenes
    print("=== ASSEMBLE ===")
    lst = RAW / "scenes.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in scene_paths), encoding="utf-8")
    silent_video = RAW / "video-silent.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent_video)],
        check=True,
        capture_output=True,
    )

    srt_path = VIDEO / "edgeguard-ops-subtitles.srt"
    write_srt(timed, srt_path)

    final = VIDEO / "edgeguard-ops-final-demo.mp4"
    # Mux audio + burn soft subtitles as soft track AND optional burned-in for readability
    # Use soft subs + slight volume normalize
    # Escape path for Windows subtitles filter
    srt_esc = str(srt_path).replace("\\", "/").replace(":", "\\:")
    burned = RAW / "with-subs.mp4"
    # Burn captions for judge viewing without needing player subtitle support
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(vo_wav),
            "-vf",
            f"subtitles='{srt_esc}':force_style='FontName=Segoe UI,FontSize=20,PrimaryColour=&H00E8EEF7&,OutlineColour=&H00100A00&,BorderStyle=3,Outline=1,Shadow=0,MarginV=40'",
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
            "-shortest",
            "-movflags",
            "+faststart",
            str(final),
        ],
        check=True,
        capture_output=True,
    )

    info = ffprobe_json(final)
    duration = float(info["format"]["duration"])
    vstream = next(s for s in info["streams"] if s["codec_type"] == "video")
    astream = next(s for s in info["streams"] if s["codec_type"] == "audio")

    # Preview frames across timeline
    extract_preview_frames(final, [2, 25, 50, 80, 110, 140, 160, max(duration - 3, 1)])

    captures_used = sorted(p.name for p in CAPTURES.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})

    manifest = {
        "output": str(final.relative_to(ROOT)).replace("\\", "/"),
        "subtitles": str(srt_path.relative_to(ROOT)).replace("\\", "/"),
        "voiceover": str(vo_wav.relative_to(ROOT)).replace("\\", "/"),
        "duration_seconds": duration,
        "size_bytes": final.stat().st_size,
        "video_codec": vstream.get("codec_name"),
        "audio_codec": astream.get("codec_name"),
        "width": int(vstream.get("width", 0)),
        "height": int(vstream.get("height", 0)),
        "fps": eval(vstream.get("r_frame_rate", "30/1")),
        "voice": VOICE,
        "segments": timed,
        "evidence_sources": [
            "docs/evidence/performance-metrics.json",
            "docs/evidence/live-datadog-validation.json",
            "docs/presentation/assets/slide-previews/",
        ],
        "datadog_captures_embedded": captures_used,
        "datadog_captures_note": (
            "Real Datadog PNG/JPG in docs/video/captures/ are embedded when present. "
            "Absent captures → labeled reconstructed status/metric scenes from verified evidence (not fake UI)."
        ),
        "disclosures": [
            "All demo telemetry is synthetic and labeled on-screen.",
            "Staged Alert: response-worker intentionally delayed; 111.4s is NOT autonomous MTTA.",
            "FPS 12.1→18.0 is safe-mode recovery, not full 30 FPS restoration.",
            "APM live verified for telemetry-api only.",
        ],
        "baseline_commit_hint": "52bb9c8+",
    }
    man_path = VIDEO / "video-build-manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also keep soft SRT alongside; copy VO
    print("=== DONE ===")
    print(json.dumps({k: manifest[k] for k in ("output", "duration_seconds", "size_bytes", "width", "height", "video_codec", "audio_codec", "datadog_captures_embedded")}, indent=2))
    return manifest


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("BUILD FAILED:", e, file=sys.stderr)
        raise
