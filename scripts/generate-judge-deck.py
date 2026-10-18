"""Generate EdgeGuard Ops 8-slide judge deck (dark industrial)."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "docs" / "presentation" / "EdgeGuard-Ops-Judge-Deck.pptx"

BG = RGBColor(0x0B, 0x12, 0x20)
FG = RGBColor(0xE8, 0xEE, 0xF7)
MUTED = RGBColor(0x9A, 0xA8, 0xBC)
ACCENT = RGBColor(0x3D, 0xDC, 0x97)
CARD = RGBColor(0x14, 0x1E, 0x30)


def paint(slide, prs):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG
    shape.line.fill.background()
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.12), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def add_text(slide, left, top, width, height, text, size=28, bold=False, color=FG, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return box


def bullets(slide, left, top, width, height, lines, size=20):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        run = p.add_run()
        run.text = "•  " + line
        run.font.size = Pt(size)
        run.font.color.rgb = FG
        run.font.name = "Calibri"
    return box


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(2.0), Inches(12), Inches(1), "EdgeGuard Ops", 48, True)
    add_text(
        s,
        Inches(0.7),
        Inches(3.0),
        Inches(12),
        Inches(0.6),
        "Signal404  ·  MUGVN Hackathon 2026 — Real-time Operations",
        22,
        False,
        MUTED,
    )
    add_text(
        s,
        Inches(0.7),
        Inches(4.0),
        Inches(11),
        Inches(1),
        "Detect → Investigate → Respond → Verify\nfor edge AI camera fleets",
        26,
    )
    add_text(
        s,
        Inches(0.7),
        Inches(6.6),
        Inches(12),
        Inches(0.4),
        "MongoDB time-series control plane  ·  Datadog operator plane",
        14,
        False,
        MUTED,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "The Problem", 36, True)
    bullets(
        s,
        Inches(0.7),
        Inches(1.6),
        Inches(11.5),
        Inches(4.5),
        [
            "Edge GPUs thermally throttle — FPS collapses and frames drop before operators notice",
            "Symptoms can look like slow inference or a network fault",
            "Teams need proof of root cause and proof of recovery — not more raw charts",
            "Without a closed loop, fleet telemetry is just expensive noise",
        ],
        22,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "Our Solution", 36, True)
    steps = [
        ("Detect", "$setWindowFields thermal trends"),
        ("Investigate", "Evidence + calm network contrast"),
        ("Respond", "Commanded safe profile"),
        ("Verify", "Continuous healthy reported-safe samples"),
    ]
    for i, (title, body) in enumerate(steps):
        x = Inches(0.7 + i * 3.1)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.2), Inches(2.9), Inches(3.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD
        card.line.color.rgb = ACCENT
        add_text(s, x + Inches(0.2), Inches(2.5), Inches(2.5), Inches(0.6), title, 22, True, ACCENT)
        add_text(s, x + Inches(0.2), Inches(3.3), Inches(2.5), Inches(1.8), body, 16)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "System Architecture", 36, True)
    arch = (
        "Simulator → Telemetry API → MongoDB Time Series\n"
        "                ↓                         ↓\n"
        "         Datadog Agent            Health Analyzer (poll)\n"
        "                                          ↓\n"
        "                                   Incidents\n"
        "                                          ↓\n"
        "                            Response Worker (poll)\n"
        "                                          ↓\n"
        "                     commanded safe → continuous evidence → RESOLVED"
    )
    add_text(s, Inches(0.7), Inches(1.5), Inches(12), Inches(4.5), arch, 18)
    add_text(
        s,
        Inches(0.7),
        Inches(6.5),
        Inches(12),
        Inches(0.4),
        "Polling is intentional · No Kafka / Kubernetes / custom frontend",
        14,
        False,
        MUTED,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "Intelligent Incident Detection", 34, True)
    bullets(
        s,
        Inches(0.7),
        Inches(1.6),
        Inches(11.5),
        Inches(4.5),
        [
            "Short vs trailing windows on GPU temperature, inference latency, and FPS",
            "Packet loss / network latency checked so thermal is not mislabeled as network",
            "Incident document stores evidence snapshot + root-cause text",
            "MongoDB aggregation is the analytical source of truth — not a bolt-on cache",
        ],
        22,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "Automated Remediation", 36, True)
    bullets(
        s,
        Inches(0.7),
        Inches(1.6),
        Inches(11.5),
        Inches(4.5),
        [
            "Poll active incidents → atomic $set of commanded_profile=safe",
            "Commanded ≠ reported — telemetry 'full' never proves the device ran 'safe'",
            "Observation window requires continuous healthy samples; stalls reset evidence",
            "Remediation reaches VERIFIED only after recovery evidence passes",
        ],
        22,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "Live Validation & Impact", 34, True)
    add_text(
        s,
        Inches(0.7),
        Inches(1.3),
        Inches(12),
        Inches(0.4),
        "Synthetic incident inc-thermal-edge-001-20261018085058 · observed 2026-10-18",
        14,
        False,
        MUTED,
    )
    rows = [
        ("Signal", "Before", "After safe"),
        ("GPU °C", "~92", "~54"),
        ("Latency ms", "~177", "~60"),
        ("FPS", "~12", "~18"),
    ]
    for r, row in enumerate(rows):
        y = Inches(1.9 + r * 0.55)
        for c, cell in enumerate(row):
            x = Inches(0.7 + c * 2.4)
            color = ACCENT if r == 0 else FG
            add_text(s, x, y, Inches(2.2), Inches(0.45), cell, 18, r == 0, color)
    bullets(
        s,
        Inches(0.7),
        Inches(4.3),
        Inches(11.5),
        Inches(2.5),
        [
            "Datadog demo monitor: ALERT → OK (live)",
            "Dashboard 9rr-a4u-2st · Monitor 333934695",
            "Staged response-worker delay for Alert visibility — disclosed, not hidden",
        ],
        18,
    )

    s = prs.slides.add_slide(prs.slide_layouts[6])
    paint(s, prs)
    add_text(s, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7), "Differentiation & Future", 34, True)
    bullets(
        s,
        Inches(0.7),
        Inches(1.5),
        Inches(11.5),
        Inches(4.5),
        [
            "Creative: commanded vs reported profiles + continuous recovery evidence",
            "Future: change streams, multi-site fleets, verify APM for all three services in UI",
            "Limitations: synthetic data; poll-interval floor; APM cloud verified for telemetry-api",
            "Closing ask: Detect → Investigate → Respond → Verify — observable and recoverable",
        ],
        20,
    )
    add_text(
        s,
        Inches(0.7),
        Inches(6.4),
        Inches(12),
        Inches(0.5),
        "Signal404 · EdgeGuard Ops · Thank you",
        18,
        True,
        ACCENT,
    )

    prs.save(OUT)
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
