# EdgeGuard Ops — 8 judge slides (source content)

Current editable PPTX: [EdgeGuard-Ops-Submission-20261106.pptx](EdgeGuard-Ops-Submission-20261106.pptx)

Original October deck retained as historical: [EdgeGuard-Ops-Judge-Deck.pptx](EdgeGuard-Ops-Judge-Deck.pptx)
The original Python generator produces the historical deck. Current content was edited with the bundled presentation tool; source edits and validation receipt are in local ignored `artifacts/submission-qa/deck/`. Do not regenerate the submission deck using the old generator.
Style: dark (#0B1220), text #E8EEF7, accent #3DDC97, alert #FF6B4A.
All telemetry on slides is **synthetic** and labeled.

---

## Slide 1 — Title

**EdgeGuard Ops** · Closed-loop observability for edge AI camera fleets
Visual: Detect → Investigate → Respond → Verify nodes
Footer: Signal404 · MongoDB + Datadog · Synthetic demo data labeled throughout

## Slide 2 — The Problem

Three cards: Thermal throttle · Misread symptoms · No closed loop
Need: early detection → safe action → proof the fleet is healthy again

## Slide 3 — Our Solution

Four cards: Detect / Investigate / Respond / Verify
Pill: **SYNTHETIC TELEMETRY LAB RUN**
Note: safe mode ≠ full 30 FPS restore

## Slide 4 — System Architecture

**Visual diagram** (not ASCII): Simulator → Telemetry API → MongoDB TS → Health Analyzer → Response Worker; Datadog as operator lens
Design choices card: polling, commanded ≠ reported, no Kafka/K8s/custom UI, DogStatsD + file-tail

## Slide 5 — Intelligent Incident Detection

Windows → Contrast → Open
Automatic run `20261021202014`: **4.713 s** detection→request; **29.824 s** detection→resolved. Single synthetic run, not a production benchmark. Short startup uses the absolute heat threshold; no full five-minute baseline is claimed.

## Slide 6 — Automated Remediation

Commanded vs reported · Verify recovery
SAFE MODE = thermal headroom trade-off · post-recovery FPS ≈ 18, not 30.
Automatic run: RESOLVED / VERIFIED / safe; captured sample 54.73°C / 18 FPS.

## Slide 7 — Historical staged validation (October 18)

Metric bars from evidence: GPU **92.3→54.1°C**, latency **177.3→59.6 ms**, FPS **12.1→18.0**
Timeline (staged Alert): 40.9s detect · **111.4s includes intentional worker delay (NOT autonomous MTTA)** · 18.2s VERIFIED
APM live: telemetry-api only · Incident …85058
Optional real Datadog PNGs if present under `assets/` (none fabricated)

## Slide 8 — Why EdgeGuard Ops

Creative / Technical / Impact / Honest pillars
Monitoring detects the problem. EdgeGuard acts on it and verifies recovery.
Public repo · publish audited release · Deadline 8 Nov 2026, 23:59 ICT

November 7: current deck footer reconciled with public visibility; original October deck remains historical. Runtime validation remains tied to 40ee9ee, not to the October video.
