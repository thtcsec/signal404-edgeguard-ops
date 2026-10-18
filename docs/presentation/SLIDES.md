# EdgeGuard Ops — 8 judge slides (source content)

Editable PPTX: [EdgeGuard-Ops-Judge-Deck.pptx](EdgeGuard-Ops-Judge-Deck.pptx)  
Style: dark industrial (#0B1220 background, #E8EEF7 text, #3DDC97 accent, #FF6B4A alert).

---

## Slide 1 — EdgeGuard Ops

**Title:** EdgeGuard Ops  
**Subtitle:** Signal404 · MUGVN Hackathon 2026  
**Line:** Detect → Investigate → Respond → Verify for edge AI camera fleets  
**Footer:** MongoDB time-series + Datadog operator plane

## Slide 2 — The Problem

- Edge GPUs thermally throttle → FPS collapse, frames drop  
- Symptoms look like “slow inference” or “bad network”  
- Operators need proof of cause **and** proof of recovery  
- **Without a closed loop, telemetry is just noise**

## Slide 3 — Our Solution

Four beats only:

1. **Detect** — `$setWindowFields` thermal trends  
2. **Investigate** — evidence + calm network contrast  
3. **Respond** — commanded `safe` profile  
4. **Verify** — continuous healthy reported-safe samples  

## Slide 4 — System Architecture

```
Simulator → Telemetry API → MongoDB TS
                 ↓               ↓
            Datadog Agent   Health Analyzer (poll)
                                 ↓
                            Incidents → Response Worker (poll)
                                 ↓
                         safe profile → RESOLVED
```

Polling is intentional. No Kafka / K8s / custom UI.

## Slide 5 — Intelligent Incident Detection

- Short vs trailing windows: GPU °C, latency, FPS  
- Packet loss / network latency checked to avoid false “network” blame  
- Incident stores evidence snapshot + root-cause text  
- **MongoDB is the analytical source of truth**

## Slide 6 — Automated Remediation

- Poll active incidents → atomic `$set` commanded profile  
- Commanded ≠ reported (telemetry `full` ≠ proof of `safe`)  
- Observation window: continuous healthy samples; stall resets  
- Remediation `VERIFIED` only after evidence

## Slide 7 — Live Validation & Impact

**Observed (synthetic run 2026-10-18):**

| Signal | Before | After safe |
| --- | --- | --- |
| GPU °C | ~92 | ~54 |
| Latency ms | ~177 | ~60 |
| FPS | ~12 | ~18 |

- Datadog demo monitor: **ALERT → OK**  
- Dashboard / monitor live URLs in evidence JSON  
- Staged worker delay for Alert visibility — disclosed  

## Slide 8 — Differentiation & Future

**Why us:** closed-loop edge ops with honest commanded/reported + recovery evidence  
**Future:** change streams, multi-site fleets, verify APM for all three services in UI  
**Limitations:** synthetic data; poll latency floor  
**Ask:** Detect → Investigate → Respond → Verify — observable and recoverable
