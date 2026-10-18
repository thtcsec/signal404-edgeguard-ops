"""Generate EdgeGuard Ops 8-slide judge deck — visual, minimal text, evidence-accurate."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "docs" / "presentation" / "EdgeGuard-Ops-Judge-Deck.pptx"
ASSETS = Path(__file__).resolve().parents[1] / "docs" / "presentation" / "assets"

BG = RGBColor(0x0B, 0x12, 0x20)
FG = RGBColor(0xE8, 0xEE, 0xF7)
MUTED = RGBColor(0x8B, 0x9B, 0xB0)
ACCENT = RGBColor(0x3D, 0xDC, 0x97)
ALERT = RGBColor(0xFF, 0x6B, 0x4A)
CARD = RGBColor(0x14, 0x1E, 0x30)
CARD2 = RGBColor(0x1A, 0x27, 0x3D)
LINE = RGBColor(0x2A, 0x3A, 0x52)
WARN = RGBColor(0xF0, 0xC0, 0x4A)


def set_run(run, text, size, bold=False, color=FG):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


def paint(slide, prs):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG
    shape.line.fill.background()
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.1), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def label(slide, left, top, width, height, text, size=14, bold=False, color=FG, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    set_run(p.add_run(), text, size, bold, color)
    return box


def pill(slide, left, top, width, height, text, fill=ACCENT, text_color=BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.5
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = False
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    set_run(tf.paragraphs[0].add_run(), text, 11, True, text_color)
    shape.text_frame.auto_size = None
    for p in tf.paragraphs:
        p.space_before = Pt(0)
        p.space_after = Pt(0)
    return shape


def card_box(slide, left, top, width, height, title, body, accent=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.08
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = accent
    shape.line.width = Pt(1.25)
    label(slide, left + Inches(0.18), top + Inches(0.18), width - Inches(0.3), Inches(0.35), title, 16, True, accent)
    label(slide, left + Inches(0.18), top + Inches(0.55), width - Inches(0.3), height - Inches(0.7), body, 13, False, FG)
    return shape


def node(slide, left, top, width, height, title, subtitle="", fill=CARD2):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = 0.12
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = ACCENT
    shape.line.width = Pt(1.5)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    set_run(tf.paragraphs[0].add_run(), title, 14, True, FG)
    if subtitle:
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), subtitle, 11, False, MUTED)
    return shape


def arrow_right(slide, x1, y, x2):
    """Simple chevron as a right-pointing triangle strip."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x1, y - Inches(0.12), x2 - x1, Inches(0.24))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    return shape


def metric_bars(slide, left, top, width, title, before, after, unit, max_val, better="lower"):
    """Horizontal before/after bars with fixed-width value column (no overflow into timeline)."""
    label(slide, left, top, width, Inches(0.3), title, 14, True, FG)
    row_label_w = Inches(0.95)
    value_w = Inches(1.35)
    bar_area = width - row_label_w - value_w - Inches(0.1)
    bar_left = left + row_label_w

    label(slide, left, top + Inches(0.35), row_label_w, Inches(0.25), "Before", 11, False, MUTED)
    bw = max(Inches(0.15), bar_area * (before / max_val))
    bar1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bar_left, top + Inches(0.35), bw, Inches(0.28))
    bar1.adjustments[0] = 0.4
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = ALERT
    bar1.line.fill.background()
    label(slide, left + width - value_w, top + Inches(0.35), value_w, Inches(0.28), f"{before}{unit}", 12, True, ALERT)

    label(slide, left, top + Inches(0.75), row_label_w, Inches(0.25), "After", 11, False, MUTED)
    aw = max(Inches(0.15), bar_area * (after / max_val))
    bar2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bar_left, top + Inches(0.75), aw, Inches(0.28))
    bar2.adjustments[0] = 0.4
    bar2.fill.solid()
    bar2.fill.fore_color.rgb = ACCENT
    bar2.line.fill.background()
    label(slide, left + width - value_w, top + Inches(0.75), value_w, Inches(0.28), f"{after}{unit}", 12, True, ACCENT)


def footer(slide, text="Synthetic telemetry · Signal404 · EdgeGuard Ops"):
    label(slide, Inches(0.5), Inches(7.05), Inches(12), Inches(0.3), text, 11, False, MUTED)


def try_add_image(slide, path: Path, left, top, width, height):
    if path.is_file():
        slide.shapes.add_picture(str(path), left, top, width=width, height=height)
        return True
    return False


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # --- Slide 1 ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    pill(s, Inches(0.6), Inches(1.6), Inches(2.4), Inches(0.35), "MUGVN 2026", ACCENT, BG)
    label(s, Inches(0.6), Inches(2.2), Inches(12), Inches(0.9), "EdgeGuard Ops", 52, True, FG)
    label(
        s,
        Inches(0.6),
        Inches(3.2),
        Inches(11),
        Inches(0.8),
        "Closed-loop observability for edge AI camera fleets",
        24,
        False,
        MUTED,
    )
    # four beats
    beats = ["Detect", "Investigate", "Respond", "Verify"]
    for i, b in enumerate(beats):
        x = Inches(0.6 + i * 3.0)
        node(s, x, Inches(4.5), Inches(2.7), Inches(1.1), b, "" if i < 3 else "recovery evidence")
        if i < 3:
            arrow_right(s, x + Inches(2.75), Inches(5.0), x + Inches(2.95))
    footer(s, "Signal404  ·  MongoDB + Datadog  ·  Synthetic demo data labeled throughout")

    # --- Slide 2 Problem ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.4), Inches(12), Inches(0.6), "The Problem", 34, True)
    # three problem cards
    problems = [
        ("Thermal throttle", "GPU heat silently cuts\ninference quality"),
        ("Misread symptoms", "Looks like latency or\nnetwork — until it isn’t"),
        ("No closed loop", "Alerts without verified\nrecovery leave risk open"),
    ]
    for i, (t, b) in enumerate(problems):
        card_box(s, Inches(0.6 + i * 4.1), Inches(1.5), Inches(3.85), Inches(2.6), t, b, ALERT if i == 0 else ACCENT)
    label(
        s,
        Inches(0.6),
        Inches(4.6),
        Inches(12),
        Inches(1.2),
        "Operators need: early detection → safe action → proof the fleet is healthy again.",
        20,
        False,
        FG,
    )
    footer(s)

    # --- Slide 3 Solution ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.4), Inches(12), Inches(0.55), "Our Solution", 34, True)
    steps = [
        ("1  Detect", "$setWindowFields\nthermal trends"),
        ("2  Investigate", "Evidence + calm\nnetwork contrast"),
        ("3  Respond", "Commanded\nsafe profile"),
        ("4  Verify", "Continuous healthy\nreported-safe samples"),
    ]
    for i, (t, b) in enumerate(steps):
        card_box(s, Inches(0.5 + i * 3.2), Inches(1.4), Inches(3.0), Inches(3.4), t, b)
    pill(s, Inches(0.6), Inches(5.3), Inches(4.2), Inches(0.4), "SYNTHETIC TELEMETRY LAB RUN", WARN, BG)
    label(
        s,
        Inches(5.0),
        Inches(5.3),
        Inches(7.5),
        Inches(0.8),
        "Safe mode trades peak FPS for thermal headroom — recovery ≠ full 30 FPS restore.",
        15,
        False,
        MUTED,
    )
    footer(s)

    # --- Slide 4 Architecture (visual) ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.5), "System Architecture", 32, True)

    # Row 1
    node(s, Inches(0.5), Inches(1.3), Inches(2.4), Inches(1.0), "Simulator", "synthetic devices")
    arrow_right(s, Inches(3.0), Inches(1.75), Inches(3.35))
    node(s, Inches(3.4), Inches(1.3), Inches(2.6), Inches(1.0), "Telemetry API", ".NET ingest")
    arrow_right(s, Inches(6.1), Inches(1.75), Inches(6.45))
    node(s, Inches(6.5), Inches(1.3), Inches(3.0), Inches(1.0), "MongoDB TS", "TTL + windows")
    # Datadog side
    node(s, Inches(10.1), Inches(1.3), Inches(2.6), Inches(1.0), "Datadog", "metrics · logs · monitor", CARD)

    # arrows down from mongo
    down = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(7.6), Inches(2.45), Inches(0.35), Inches(0.45))
    down.fill.solid()
    down.fill.fore_color.rgb = ACCENT
    down.line.fill.background()

    node(s, Inches(5.8), Inches(3.1), Inches(3.4), Inches(1.0), "Health Analyzer", "poll · $setWindowFields")
    down2 = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(7.6), Inches(4.25), Inches(0.35), Inches(0.4))
    down2.fill.solid()
    down2.fill.fore_color.rgb = ACCENT
    down2.line.fill.background()

    node(s, Inches(5.8), Inches(4.8), Inches(3.4), Inches(1.0), "Response Worker", "poll · safe profile · verify")

    # side notes
    card_box(
        s,
        Inches(0.5),
        Inches(3.1),
        Inches(4.8),
        Inches(2.7),
        "Design choices",
        "• Polling (not change streams)\n• Commanded ≠ reported profile\n• No Kafka / K8s / custom UI\n• DogStatsD + file-tail logs",
        LINE,
    )
    label(s, Inches(10.0), Inches(3.0), Inches(2.8), Inches(2.5), "MongoDB = truth\nDatadog = operator lens", 16, True, MUTED)
    footer(s)

    # --- Slide 5 Detection ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.5), "Intelligent Incident Detection", 30, True)
    # timeline visual
    phases = [
        ("Windows", "1m vs trailing 5m\nGPU · latency · FPS"),
        ("Contrast", "Packet loss &\nnet latency calm?"),
        ("Open", "Incident + evidence\nsnapshot"),
    ]
    for i, (t, b) in enumerate(phases):
        x = Inches(0.6 + i * 4.2)
        card_box(s, x, Inches(1.3), Inches(3.9), Inches(2.8), t, b)
        if i < 2:
            arrow_right(s, x + Inches(3.95), Inches(2.5), x + Inches(4.15))
    label(
        s,
        Inches(0.6),
        Inches(4.5),
        Inches(12),
        Inches(1.2),
        "Detection clock we publish: first stored sample → incident.detectedAt ≈ 40.9s\n"
        "(not “seconds since anomaly onset” — heat ramps inside the simulator).",
        16,
        False,
        MUTED,
    )
    footer(s)

    # --- Slide 6 Remediation ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.35), Inches(12), Inches(0.5), "Automated Remediation", 32, True)
    # two columns: commanded vs reported
    card_box(
        s,
        Inches(0.5),
        Inches(1.2),
        Inches(6.0),
        Inches(3.2),
        "Commanded vs reported",
        "Worker sets commanded_profile = safe\nSimulator applies and reports reported_profile\n\nTelemetry “full” never proves the device ran “safe”.",
        ACCENT,
    )
    card_box(
        s,
        Inches(6.8),
        Inches(1.2),
        Inches(5.9),
        Inches(3.2),
        "Verify recovery",
        "Continuous healthy reported-safe samples\nStale / gap telemetry resets the window\n\nVERIFIED only after evidence — not a timer alone.",
        ACCENT,
    )
    pill(s, Inches(0.6), Inches(4.8), Inches(5.5), Inches(0.4), "SAFE MODE = THERMAL HEADROOM TRADE-OFF", WARN, BG)
    label(
        s,
        Inches(0.6),
        Inches(5.4),
        Inches(12),
        Inches(0.9),
        "Observed post-recovery FPS ≈ 18 — intentional safe operating point, not a claim of full 30 FPS restoration.",
        16,
        False,
        FG,
    )
    footer(s)

    # --- Slide 7 Impact ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.3), Inches(10), Inches(0.45), "Live Validation & Impact", 30, True)
    pill(s, Inches(10.2), Inches(0.35), Inches(2.5), Inches(0.35), "SYNTHETIC RUN", WARN, BG)

    metric_bars(s, Inches(0.5), Inches(1.0), Inches(5.8), "GPU temperature", 92.3, 54.1, "°C", 100)
    metric_bars(s, Inches(0.5), Inches(2.35), Inches(5.8), "Inference latency", 177.3, 59.6, " ms", 200)
    metric_bars(s, Inches(0.5), Inches(3.7), Inches(5.8), "FPS (safe ≠ full)", 12.1, 18.0, "", 30)

    # timeline card
    card_box(
        s,
        Inches(6.8),
        Inches(1.0),
        Inches(5.9),
        Inches(4.5),
        "Incident timeline (staged Alert demo)",
        "• 40.9s  first sample → detect\n"
        "• 111.4s detect → remediate request\n"
        "     ↳ includes intentional worker delay\n"
        "     ↳ NOT autonomous MTTA\n"
        "• 18.2s  remediate → VERIFIED\n\n"
        "Datadog demo monitor: ALERT → OK\n"
        "APM live: telemetry-api only\n"
        "Incident: …85058  ·  Device: edge-001",
        LINE,
    )
    # optional screenshots
    dash = ASSETS / "datadog-dashboard.png"
    mon = ASSETS / "datadog-monitor-ok.png"
    y_img = Inches(5.5)
    if try_add_image(s, dash, Inches(0.5), y_img, Inches(5.8), Inches(1.35)):
        label(s, Inches(0.5), Inches(6.85), Inches(5.8), Inches(0.25), "Live dashboard capture", 10, False, MUTED)
    footer(s, "Evidence: docs/evidence/performance-metrics.json + live-datadog-validation.json")

    # --- Slide 8 ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    label(s, Inches(0.6), Inches(0.4), Inches(12), Inches(0.55), "Why EdgeGuard Ops", 32, True)
    reasons = [
        ("Creative", "Commanded ≠ reported\nContinuous recovery evidence"),
        ("Technical", "MongoDB windows + TTL\nDatadog ALERT → OK live"),
        ("Impact", "Measured safe-mode recovery\non a full Detect→Verify loop"),
        ("Honest", "Synthetic labeled\nStaged Alert disclosed"),
    ]
    for i, (t, b) in enumerate(reasons):
        card_box(s, Inches(0.5 + i * 3.2), Inches(1.3), Inches(3.0), Inches(3.0), t, b)
    label(
        s,
        Inches(0.6),
        Inches(4.7),
        Inches(12),
        Inches(0.8),
        "Finals scoring (official): Creativity 30% · Technical 30% · Impact 30% · Presentation 10%",
        16,
        False,
        MUTED,
    )
    label(s, Inches(0.6), Inches(5.6), Inches(12), Inches(0.6), "Detect → Investigate → Respond → Verify", 26, True, ACCENT)
    label(s, Inches(0.6), Inches(6.3), Inches(12), Inches(0.4), "Signal404 · Thank you", 18, False, FG)
    footer(s, "Repo private through 22 Nov 2026 · Submit by 31 Oct 2026 23:59 ICT")

    prs.save(OUT)
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    build()
