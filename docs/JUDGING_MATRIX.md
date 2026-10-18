# Judging matrix — EdgeGuard Ops

**Official public finals weights (confirmed):** Creativity **30%** · Technical **30%** · Impact **30%** · Presentation **10%**.

| Criterion | Weight | What we claim | Evidence | Risk if overstated |
| --- | --- | --- | --- | --- |
| **Creativity** | 30% | Closed-loop edge fleet ops: commanded vs reported profiles; continuous recovery evidence; thermal-vs-network differentiation | Code: `SafeProfileRemediationExecutor`, `RecoveryEvidence`; [INCIDENT_SCENARIO.md](INCIDENT_SCENARIO.md) | Claiming “AI agent” or novel ML — we do **not** |
| **Technical** | 30% | Real MongoDB time-series + `$setWindowFields`; DogStatsD + logs + monitor ALERT→OK; .NET APM Bundle | Tests; [live-datadog-validation.json](evidence/live-datadog-validation.json) | Claiming full 3-service APM — only **telemetry-api** verified live |
| **Impact** | 30% | Measured synthetic recovery: GPU 92.3→54.1°C, latency 177.3→59.6 ms, FPS 12.1→18.0 (safe mode ≠ 30 FPS); Alert→OK | [performance-metrics.json](evidence/performance-metrics.json) | Presenting 111.4s as autonomous MTTA; claiming production ROI or full FPS restore |
| **Presentation** | 10% | Visual 8-slide deck + 3-min VI script + recording sequence | [presentation/](presentation/), [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md), [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md) | Slides without live evidence; fabricating DD screenshots |

## Creativity — talking points

- Separates **commanded** vs **reported** profiles.
- Recovery is evidence-based (continuous healthy samples), not timer-only.
- Root cause contrasts thermal degradation with calm network metrics.

## Technical — talking points

- MongoDB = control / truth plane; Datadog = operator lens.
- Repo-reproducible dashboard/monitor JSON + apply script.
- Polling workers are intentional for the demo scope.

## Impact — talking points

- Synthetic run `inc-thermal-edge-001-20261018085058`: GPU / latency / FPS deltas above.
- 40.9s = first stored sample → detect; 111.4s includes staged worker delay.
- Monitor ALERT → OK observed live on demo monitor.

## Presentation — talking points

- One incident, one device (`edge-001`), one dashboard, one monitor.
- Explicit staged Alert disclosure; separate automatic E2E plan documented.
