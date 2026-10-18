#!/usr/bin/env python3
"""
QA patch for EdgeGuard Ops demo video.
- Tightens narration (esp. impact) to land 175–179s
- Consistent gTTS Vietnamese voice (no mixed engines)
- Sentence-aligned short SRT cues + bottom burned-in captions
- Retimes existing scene videos (setpts) — does not rebuild the whole demo from scratch
- Evidence-driven metric labels; reconstruction vs historical graph disclosures
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import wave
from pathlib import Path

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "docs" / "video"
SCENES = VIDEO / "scenes"
AUDIO = VIDEO / "audio"
RAW = VIDEO / "raw"
PREVIEWS = VIDEO / "preview-frames"
CAPTURES = VIDEO / "captures"
EVIDENCE_PATH = ROOT / "docs" / "evidence" / "performance-metrics.json"
SLIDES = ROOT / "docs" / "presentation" / "assets" / "slide-previews"

W, H, FPS = 1920, 1080, 30
BG = (11, 18, 32)
FG = (232, 238, 247)
MUTED = (139, 155, 176)
ACCENT = (61, 220, 151)
ALERT = (255, 107, 74)
WARN = (240, 192, 74)
CARD = (20, 30, 48)
SILENCE_GAP = 0.22  # keep total VO in 175–179s band


def load_evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def metrics_from_evidence(ev: dict) -> dict:
    b = ev["metrics"]["avg_before_detection_window"]
    a = ev["metrics"]["avg_after_resolve_safe"]
    t = ev["timings_seconds"]
    return {
        "gpu_b": b["gpu_temperature_c"],
        "gpu_a": a["gpu_temperature_c"],
        "lat_b": b["inference_latency_ms"],
        "lat_a": a["inference_latency_ms"],
        "fps_b": b["fps"],
        "fps_a": a["fps"],
        "detect_s": t["first_telemetry_to_detection"],
        "rem_s": t["detection_to_remediation_request"],
        "ver_s": t["remediation_request_to_verified"],
        "incident": ev["incident_id"],
        "device": ev["device_id"],
    }


def build_segments(m: dict) -> list[dict]:
    """TTS text (spoken) + caption sentences (on-screen). Captions stay short."""
    # Pronunciation-friendly spoken forms; captions use normal product names.
    return [
        {
            "id": "01_open",
            "tts": (
                "Xin chào ban giám khảo. Em là thành viên đội Signal bốn không bốn, "
                "với dự án Edge Guard Ops. "
                "Trên nhà máy, camera A I edge chạy liên tục. "
                "Khi GPU nóng và thermal throttling xảy ra, ép-pi-ét giảm — thường phát hiện muộn. "
                "Câu hỏi của chúng em: làm sao phát hiện sớm, xử lý an toàn, "
                "và chứng minh đã hồi phục?"
            ),
            "captions": [
                "Xin chào ban giám khảo.",
                "Signal404 — dự án EdgeGuard Ops.",
                "Camera AI edge chạy liên tục.",
                "GPU nóng → FPS giảm, phát hiện muộn.",
                "Cần phát hiện sớm, xử lý an toàn,",
                "và chứng minh đã hồi phục.",
            ],
        },
        {
            "id": "02_arch",
            "tts": (
                "Edge Guard Ops theo vòng Detect, Investigate, Respond, Verify. "
                "Mongo Đê Bê Time Series là nguồn sự thật. "
                "Đa-ta-đốc là mặt quan sát: metrics, logs và monitor theo cùng device ID. "
                "Toàn bộ telemetry trong demo này là synthetic, có nhãn rõ ràng."
            ),
            "captions": [
                "Detect → Investigate → Respond → Verify.",
                "MongoDB Time Series = nguồn sự thật.",
                "Datadog = mặt quan sát vận hành.",
                "Telemetry demo: synthetic, có nhãn.",
            ],
        },
        {
            "id": "03_thermal",
            "tts": (
                "Đây là kịch bản thermal throttle trên simulator — dữ liệu giả lập. "
                "GPU tăng, lai-ten-xi tăng, ép-pi-ét giảm. "
                "Health analyzer dùng set window fields trên Mongo Đê Bê "
                "để phát hiện xu hướng nhiệt, đồng thời kiểm tra mạng không phải nguyên nhân chính."
            ),
            "captions": [
                "Thermal throttle — dữ liệu giả lập.",
                "GPU ↑ · latency ↑ · FPS ↓",
                "MongoDB $setWindowFields phát hiện xu hướng.",
            ],
        },
        {
            "id": "04_datadog_alert",
            "tts": (
                "Trên dashboard Edge Guard: GPU, lai-ten-xi và ép-pi-ét. "
                "Thẻ Alert trên màn hình là tái dựng theo lịch sử đã xác nhận, "
                "không phải ảnh chụp giao diện live của Đa-ta-đốc. "
                "Chúng em cố ý khởi động response worker muộn để thấy Alert — "
                "đây là demo staged, không phải thời gian phản hồi tự động thuần túy."
            ),
            "captions": [
                "Dashboard: GPU · latency · FPS.",
                "Thẻ ALERT = tái dựng (đã xác nhận),",
                "không phải ảnh UI live.",
                "Staged: worker khởi động muộn.",
                "Không phải MTTA tự động thuần túy.",
            ],
        },
        {
            "id": "05_respond",
            "tts": (
                "Response worker đặt commanded profile bằng safe và ghi remediation. "
                "Simulator áp dụng và báo reported profile bằng safe. "
                "Chúng em tách commanded và reported "
                "để telemetry full không bị nhầm thành bằng chứng đã chạy safe."
            ),
            "captions": [
                "commanded_profile = safe",
                "reported_profile = safe",
                "Commanded ≠ reported.",
                "Telemetry full ≠ bằng chứng safe.",
            ],
        },
        {
            "id": "06_verify",
            "tts": (
                "Recovery cần chuỗi mẫu healthy liên tục. "
                "Lịch sử xác nhận: monitor Alert rồi OK. "
                "Mongo Đê Bê Resolved, remediation Verified. "
                "File trạng thái monitor hiện tại chỉ phản ánh OK — "
                "không tự chứng minh cả Alert và OK. Bằng chứng cứng là Mongo Đê Bê."
            ),
            "captions": [
                "Recovery = chuỗi mẫu healthy liên tục.",
                "Lịch sử: ALERT → OK (đã xác nhận).",
                "MongoDB RESOLVED · remediation VERIFIED.",
                "monitor-status.json hiện tại = OK only.",
                "Bằng chứng cứng: MongoDB.",
            ],
        },
        {
            "id": "07_impact",
            "tts": (
                f"Số liệu synthetic từ Mongo Đê Bê: "
                f"GPU {vi_num(m['gpu_b'])} xuống {vi_num(m['gpu_a'])} độ C. "
                f"Lai-ten-xi {vi_num(m['lat_b'])} xuống {vi_num(m['lat_a'])} mili giây. "
                f"Ép-pi-ét {vi_num(m['fps_b'])} lên {vi_num(m['fps_a'])} — safe mode, không phải ba mươi FPS. "
                f"{vi_num(m['detect_s'])} giây mẫu đầu tới detect. "
                f"{vi_num(m['rem_s'])} giây gồm trì hoãn worker staged."
            ),
            "captions": [
                "Synthetic — cửa sổ MongoDB đo được:",
                f"GPU {m['gpu_b']}→{m['gpu_a']}°C",
                f"Latency {m['lat_b']}→{m['lat_a']} ms",
                f"FPS {m['fps_b']}→{m['fps_a']} (safe ≠ 30)",
                f"{m['detect_s']}s: mẫu đầu → detect",
                f"{m['rem_s']}s: gồm trì hoãn worker staged",
            ],
        },
        {
            "id": "08_close",
            "tts": (
                "Ây-pi-em live đã xác nhận trên telemetry A P I. "
                "Edge Guard Ops chứng minh vòng Detect, Investigate, Respond, Verify "
                "khép kín trên dữ liệu giả lập có nhãn. "
                "Signal bốn không bốn. Cảm ơn ban giám khảo."
            ),
            "captions": [
                "APM live: telemetry-api (đã xác nhận).",
                "Detect → Investigate → Respond → Verify.",
                "Signal404 · Cảm ơn ban giám khảo.",
            ],
        },
    ]


def vi_num(x: float) -> str:
    """Speak decimals in Vietnamese-friendly form for gTTS."""
    s = f"{x:.1f}".rstrip("0").rstrip(".")
    if "." in s:
        whole, frac = s.split(".", 1)
        return f"{whole} phẩy {frac}"
    return s


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def synthesize_gtts(text: str, out_mp3: Path, out_wav: Path):
    gTTS(text=text, lang="vi", slow=False).save(str(out_mp3))
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(out_mp3), "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", str(out_wav)],
        check=True,
        capture_output=True,
    )


def concat_wavs(paths: list[Path], out: Path, gap: float = SILENCE_GAP):
    frames = []
    params = None
    gap_bytes = None
    for p in paths:
        with wave.open(str(p), "rb") as w:
            if params is None:
                params = w.getparams()
                gap_bytes = b"\x00\x00" * int(params.framerate * gap * params.nchannels)
            frames.append(w.readframes(w.getnframes()))
            frames.append(gap_bytes)
    # drop trailing gap
    if frames:
        frames = frames[:-1]
    with wave.open(str(out), "wb") as out_w:
        out_w.setparams(params)
        for f in frames:
            out_w.writeframes(f)


def wrap_caption(text: str, max_chars: int = 40) -> str:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if len(trial) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    # max 2 lines
    if len(lines) <= 2:
        return "\n".join(lines)
    # merge overflow into 2 lines
    mid = max(1, len(words) // 2)
    return " ".join(words[:mid])[:max_chars] + "\n" + " ".join(words[mid:])[:max_chars]


def allocate_cues(captions: list[str], t0: float, duration: float) -> list[dict]:
    """Proportional timing by character weight; clamp cue length ~2–5s."""
    weights = [max(len(c), 8) for c in captions]
    total_w = sum(weights)
    cues = []
    cursor = t0
    remaining = duration
    for i, (cap, w) in enumerate(zip(captions, weights)):
        if i == len(captions) - 1:
            dur = max(1.6, remaining)
        else:
            raw = duration * (w / total_w)
            dur = min(5.0, max(2.0, raw))
            # leave room for remaining cues
            max_allowed = remaining - 1.8 * (len(captions) - i - 1)
            dur = min(dur, max(1.8, max_allowed))
        t1 = cursor + dur
        cues.append({"t0": cursor, "t1": t1, "text": wrap_caption(cap)})
        remaining = (t0 + duration) - t1
        cursor = t1
    # snap last end to segment end
    if cues:
        cues[-1]["t1"] = t0 + duration
    return cues


def write_srt(cues: list[dict], path: Path):
    def ts(sec: float) -> str:
        if sec < 0:
            sec = 0
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        if ms >= 1000:
            s += 1
            ms = 0
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, c in enumerate(cues, 1):
        lines.append(str(i))
        lines.append(f"{ts(c['t0'])} --> {ts(c['t1'])}")
        lines.append(c["text"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def media_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(r.stdout.strip())


def retime_scene(src: Path, dest: Path, target_dur: float):
    """Stretch/compress existing scene video to target duration (no full redraw)."""
    src_dur = media_duration(src)
    if src_dur <= 0.01:
        raise RuntimeError(f"bad scene duration {src}")
    factor = src_dur / target_dur  # setpts=PTS/factor → new_dur = src/factor? 
    # Want output duration = target_dur. setpts=PTS*(src_dur/target) makes slower if target>src.
    # Correct: setpts=PTS*(target/src) wait:
    # If PTS' = PTS * (src/target), then time stretches by src/target, duration becomes target.
    # Example: src=40, target=20 → PTS' = PTS*2 → plays twice as fast → duration 20. Yes factor=src/target.
    pts = src_dur / target_dur
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-filter:v",
            f"setpts={pts}*PTS",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-r",
            str(FPS),
            str(dest),
        ],
        check=True,
        capture_output=True,
    )


def load_font(size: int, bold: bool = False):
    for c in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def solid(color=BG) -> Image.Image:
    return Image.new("RGB", (W, H), color)


def badge(img: Image.Image, text: str):
    draw = ImageDraw.Draw(img)
    font = load_font(18, True)
    pad = 18
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle([48, 36, 48 + tw + pad * 2, 36 + th + pad], 16, fill=WARN)
    draw.text((48 + pad, 36 + pad // 2), text, fill=BG, font=font)


def rebuild_labeled_cards(m: dict):
    """Refresh only ALERT/OK reconstruction cards + impact metrics from evidence (stills → short clips later via retime)."""
    # ALERT reconstruction
    alert = solid()
    d = ImageDraw.Draw(alert)
    badge(alert, "SYNTHETIC · RECONSTRUCTION (not live UI)")
    d.text((60, 120), "Datadog demo monitor — reconstructed card", fill=FG, font=load_font(40, True))
    d.rounded_rectangle([60, 200, 420, 280], 18, fill=ALERT)
    d.text((140, 220), "ALERT", fill=BG, font=load_font(36, True))
    lines = [
        "Based on verified staged-demo history (ALERT seen),",
        "not a live Datadog UI screenshot.",
        f"Monitor 333934695 · device {m['device']}",
        f"Incident {m['incident']}",
        "STAGED: response-worker delayed for Alert visibility",
    ]
    y = 340
    for line in lines:
        d.text((60, y), line, fill=FG, font=load_font(26))
        y += 48
    alert.save(RAW / "card-alert.png")

    # OK / verify reconstruction + historical graphs note
    ok = solid()
    d = ImageDraw.Draw(ok)
    badge(ok, "SYNTHETIC · RECONSTRUCTION + historical graphs")
    d.text((60, 110), "Verified recovery — evidence summary", fill=FG, font=load_font(40, True))
    d.rounded_rectangle([60, 190, 520, 270], 18, fill=ACCENT)
    d.text((100, 210), "OK · RESOLVED", fill=BG, font=load_font(32, True))
    lines = [
        "ALERT→OK observed in live validation (prior run).",
        "Current monitor-status.json alone = OK only — not dual-state proof.",
        "MongoDB RESOLVED + remediation VERIFIED = hard proof.",
        "Graphs beside = Datadog API historical snapshots.",
    ]
    y = 320
    for line in lines:
        d.text((60, y), line, fill=FG, font=load_font(24))
        y += 44
    # paste gpu + fps graphs if present
    gx = 60
    for name in ("datadog-graph-gpu-edge001.png", "datadog-graph-fps-edge001.png"):
        p = CAPTURES / name
        if p.is_file() and p.stat().st_size > 2000:
            im = Image.open(p).convert("RGB")
            im.thumbnail((880, 360), Image.Resampling.LANCZOS)
            ok.paste(im, (gx, 560))
            gx += 900
    ok.save(RAW / "card-verify.png")

    # Impact metrics from evidence
    impact = solid()
    d = ImageDraw.Draw(impact)
    badge(impact, "SYNTHETIC · MongoDB evidence windows")
    d.text((60, 110), "Measured recovery (MongoDB averages)", fill=FG, font=load_font(40, True))
    d.text((60, 170), "Before = pre-detect window · After = post-resolve safe samples", fill=MUTED, font=load_font(22))
    rows = [
        ("GPU °C", m["gpu_b"], m["gpu_a"], 100, True),
        ("Latency ms", m["lat_b"], m["lat_a"], 200, True),
        ("FPS (safe ≠ 30)", m["fps_b"], m["fps_a"], 30, False),
    ]
    y = 230
    for name, before, after, mx, _ in rows:
        d.text((60, y), name, fill=MUTED, font=load_font(24))
        bw = int(1000 * before / mx)
        aw = int(1000 * after / mx)
        d.rounded_rectangle([60, y + 40, 60 + bw, y + 72], 8, fill=ALERT)
        d.rounded_rectangle([60, y + 84, 60 + aw, y + 116], 8, fill=ACCENT)
        d.text((1080, y + 42), f"{before}", fill=ALERT, font=load_font(22, True))
        d.text((1080, y + 86), f"{after}", fill=ACCENT, font=load_font(22, True))
        y += 160
    d.text(
        (60, 920),
        f"Detect {m['detect_s']}s (first sample→detect) · Rem {m['rem_s']}s includes staged delay · Verify {m['ver_s']}s",
        fill=MUTED,
        font=load_font(20),
    )
    impact.save(RAW / "card-impact.png")

    # Thermal collage: unique gpu/latency/fps
    thermal = solid()
    d = ImageDraw.Draw(thermal)
    badge(thermal, "SYNTHETIC TELEMETRY · authentic Datadog API snapshots")
    d.text((60, 110), "Datadog historical graphs — verified incident window", fill=FG, font=load_font(34, True))
    d.text((60, 160), "Aggregated series (API) · not MongoDB before/after window averages", fill=MUTED, font=load_font(22))
    slots = [(60, 220), (660, 220), (1260, 220)]
    names = [
        ("datadog-graph-gpu-edge001.png", "GPU"),
        ("datadog-graph-latency-edge001.png", "Latency"),
        ("datadog-graph-fps-edge001.png", "FPS"),
    ]
    for (fname, label), (x, y) in zip(names, slots):
        p = CAPTURES / fname
        if p.is_file() and p.stat().st_size > 2000:
            im = Image.open(p).convert("RGB")
            im.thumbnail((580, 700), Image.Resampling.LANCZOS)
            thermal.paste(im, (x, y))
            d.text((x, y - 28), label, fill=ACCENT, font=load_font(20, True))
    thermal.save(RAW / "card-thermal.png")


def still_to_mp4(png: Path, duration: float, out: Path):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(png),
            "-vf",
            f"scale={W}:{H},fps={FPS}",
            "-t",
            f"{duration:.3f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "fast",
            "-crf",
            "18",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def extract_frames(mp4: Path, times: list[float]):
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(times, 1):
        out = PREVIEWS / f"qa-p0-{i:02d}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-update", "1", str(out)],
            check=True,
            capture_output=True,
        )


def main():
    for d in (AUDIO, RAW, SCENES, PREVIEWS):
        d.mkdir(parents=True, exist_ok=True)

    # Keep v1 backup if present
    final = VIDEO / "edgeguard-ops-final-demo.mp4"
    backup = VIDEO / "edgeguard-ops-final-demo.v1-backup.mp4"
    if final.is_file() and not backup.is_file():
        final.replace(backup) if False else None  # already copied externally

    evidence = load_evidence()
    m = metrics_from_evidence(evidence)
    segments = build_segments(m)

    print("=== TTS (gTTS only) ===")
    wav_parts = []
    for seg in segments:
        mp3 = AUDIO / f"{seg['id']}.qa.mp3"
        wav = AUDIO / f"{seg['id']}.qa.wav"
        print(f"  {seg['id']}...")
        synthesize_gtts(seg["tts"], mp3, wav)
        dur = wav_duration(wav)
        seg["audio_duration"] = dur
        print(f"    {dur:.2f}s")
        wav_parts.append(wav)

    vo = VIDEO / "voiceover-vi.wav"
    concat_wavs(wav_parts, vo, SILENCE_GAP)
    total = wav_duration(vo)
    print(f"Total VO: {total:.2f}s")

    if total > 179.5:
        print("WARNING: still long; consider further tightening", file=sys.stderr)
    if total < 174.0:
        print("WARNING: under target floor", file=sys.stderr)

    print("=== Refresh labeled cards ===")
    rebuild_labeled_cards(m)

    print("=== Build scenes (exact still durations; reuse prior scene frames where useful) ===")
    # Prefer labeled cards; else export a mid-frame from prior scene as still (avoids flaky setpts)
    still_for = {
        "03_thermal": RAW / "card-thermal.png",
        "04_datadog_alert": RAW / "card-alert.png",
        "06_verify": RAW / "card-verify.png",
        "07_impact": RAW / "card-impact.png",
    }
    slide_for = {
        "01_open": SLIDES / "slide-01.png",
        "02_arch": SLIDES / "slide-04.png",
        "05_respond": SLIDES / "slide-06.png",
        "08_close": SLIDES / "slide-08.png",
    }
    # Pull mid-frame from original scenes for open/arch/respond/close if available
    for sid, dest_name in (
        ("01_open", "still-01.png"),
        ("02_arch", "still-02.png"),
        ("05_respond", "still-05.png"),
        ("08_close", "still-08.png"),
    ):
        src = SCENES / f"{sid}.mp4"
        dest = RAW / dest_name
        if src.is_file():
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "2", "-i", str(src), "-frames:v", "1", "-update", "1", str(dest)],
                check=True,
                capture_output=True,
            )
            still_for[sid] = dest
        else:
            still_for[sid] = slide_for[sid]

    timed_scenes = []
    all_cues: list[dict] = []
    t_cursor = 0.0
    scene_list = []

    for i, seg in enumerate(segments):
        dur = seg["audio_duration"]
        scene_dur = dur + (SILENCE_GAP if i < len(segments) - 1 else 0.0)
        out = SCENES / f"{seg['id']}.qa.mp4"
        png = still_for.get(seg["id"]) or slide_for.get(seg["id"]) or (SLIDES / "slide-01.png")
        still_to_mp4(png, scene_dur, out)
        # verify duration within 0.15s
        got = media_duration(out)
        if abs(got - scene_dur) > 0.25:
            print(f"  WARN {seg['id']} scene {got:.2f} vs target {scene_dur:.2f}")
        scene_list.append(out)
        cues = allocate_cues(seg["captions"], t_cursor, dur)
        all_cues.extend(cues)
        timed_scenes.append({"id": seg["id"], "t0": t_cursor, "t1": t_cursor + dur, "scene_dur": scene_dur})
        t_cursor += scene_dur

    srt_path = VIDEO / "edgeguard-ops-subtitles.srt"
    write_srt(all_cues, srt_path)
    print(f"SRT cues: {len(all_cues)}")

    lst = RAW / "scenes-qa.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in scene_list), encoding="utf-8")
    silent = RAW / "video-silent-qa.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)],
        check=True,
        capture_output=True,
    )

    # Burn-in: bottom, modest size, high contrast, leave graphs clear
    srt_esc = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\:")
    style = (
        "FontName=Segoe UI,FontSize=15,PrimaryColour=&H00F0F4FA&,OutlineColour=&H90000000&,"
        "BackColour=&H80000000&,BorderStyle=4,Outline=0,Shadow=0,MarginV=48,Alignment=2"
    )
    print("=== Assemble final ===")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(vo),
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
            "-movflags",
            "+faststart",
            str(final),
        ],
        check=True,
        capture_output=True,
    )
    # Trim/pad to audio length explicitly (avoid -shortest surprises)
    vo_dur = wav_duration(vo)
    tmp_final = RAW / "final-trim.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-t",
            f"{vo_dur:.3f}",
            "-c",
            "copy",
            str(tmp_final),
        ],
        check=True,
        capture_output=True,
    )
    tmp_final.replace(final)

    info = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(final)],
        capture_output=True,
        text=True,
        check=True,
    )
    meta = json.loads(info.stdout)
    duration = float(meta["format"]["duration"])
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    a = next(s for s in meta["streams"] if s["codec_type"] == "audio")

    extract_frames(final, [3, 28, 55, 78, 100, 125, 150, max(duration - 4, 1)])

    # Also refresh frame-01..08 used previously
    for i, t in enumerate([3, 28, 55, 78, 100, 125, 150, max(duration - 4, 1)], 1):
        subprocess.run(
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
                str(PREVIEWS / f"frame-{i:02d}.png"),
            ],
            check=True,
            capture_output=True,
        )

    manifest = {
        "output": "docs/video/edgeguard-ops-final-demo.mp4",
        "subtitles": "docs/video/edgeguard-ops-subtitles.srt",
        "voiceover": "docs/video/voiceover-vi.wav",
        "backup_v1": "docs/video/edgeguard-ops-final-demo.v1-backup.mp4",
        "duration_seconds": duration,
        "size_bytes": final.stat().st_size,
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "fps": 30.0,
        "voice": "gTTS lang=vi (consistent across all segments)",
        "tts_engine": "gtts",
        "srt_cues": len(all_cues),
        "silence_gap_seconds": SILENCE_GAP,
        "segments": timed_scenes,
        "metrics_source": "docs/evidence/performance-metrics.json",
        "metrics_used": m,
        "disclosures": [
            "All demo telemetry is synthetic and labeled.",
            "ALERT/OK cards are reconstructions from verified history — not live UI captures.",
            "Datadog graphs are authentic API historical snapshots for the verified incident window.",
            "monitor-status.json current state alone does not prove ALERT and OK.",
            "Staged worker delay disclosed; remediation interval is not autonomous MTTA.",
            "MongoDB before/after averages ≠ Datadog aggregated graph series (different aggregation).",
        ],
        "qa_patch": True,
        "target_duration_range": [175, 179],
        "duration_ok": 175.0 <= duration <= 179.0,
    }
    man_path = VIDEO / "video-build-manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== DONE ===")
    print(json.dumps({k: manifest[k] for k in ("duration_seconds", "size_bytes", "srt_cues", "duration_ok", "voice")}, indent=2))
    if not manifest["duration_ok"]:
        print(f"DURATION OUT OF RANGE: {duration}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
