# EdgeGuard Ops — 8 judge slides (source content)

Editable PPTX: [EdgeGuard-Ops-Judge-Deck.pptx](EdgeGuard-Ops-Judge-Deck.pptx)  
Generator: `scripts/generate-judge-deck.py`  
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
**40.9s** = first stored sample → `detectedAt` (not time since anomaly onset)

## Slide 6 — Automated Remediation

Commanded vs reported · Verify recovery  
SAFE MODE = thermal headroom trade-off · post-recovery FPS ≈ 18, not 30

## Slide 7 — Live Validation & Impact

Metric bars from evidence: GPU **92.3→54.1°C**, latency **177.3→59.6 ms**, FPS **12.1→18.0**  
Timeline (staged Alert): 40.9s detect · **111.4s includes intentional worker delay (NOT autonomous MTTA)** · 18.2s VERIFIED  
APM live: telemetry-api only · Incident …85058  
Optional real Datadog PNGs if present under `assets/` (none fabricated)

## Slide 8 — Why EdgeGuard Ops

Creative / Technical / Impact / Honest pillars  
Official finals scoring: Creativity 30% · Technical 30% · Impact 30% · Presentation 10%  
Repo private through 22 Nov 2026 · Submit by 31 Oct 2026 23:59 ICT
