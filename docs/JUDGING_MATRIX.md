# Judging matrix — EdgeGuard Ops

Weights below follow a common hackathon rubric (**Creativity 30% / Technical 30% / Impact 30% / Presentation 10%**). Confirm against the final official MUGVN packet if published; public posts emphasize end-to-end Detect→Investigate→Respond→Verify with MongoDB + Datadog rather than publishing a PDF rubric.

| Criterion | Weight | What we claim | Evidence | Risk if overstated |
| --- | --- | --- | --- | --- |
| **Creativity** | 30% | Closed-loop edge fleet ops: commanded vs reported profiles; continuous recovery evidence; thermal-vs-network differentiation in root cause | Code: `SafeProfileRemediationExecutor`, `RecoveryEvidence`, analyzer root-cause text; [INCIDENT_SCENARIO.md](INCIDENT_SCENARIO.md) | Claiming “AI agent” or novel ML — we do **not** |
| **Technical** | 30% | Real MongoDB time-series + `$setWindowFields`; atomic `$set`; DogStatsD + logs + monitor ALERT→OK; .NET APM Bundle | Tests; [live-datadog-validation.json](evidence/live-datadog-validation.json); dashboard/monitor JSON | Claiming full 3-service APM in Datadog UI — only **telemetry-api** verified live |
| **Impact** | 30% | Measurable synthetic incident: GPU/latency/FPS recover after safe profile; operator-visible Alert→OK | [performance-metrics.json](evidence/performance-metrics.json) | Presenting staged delay as true MTTA; claiming production ROI |
| **Presentation** | 10% | 3-min storyboard + VI script + slides + video checklist | [DEMO_STORYBOARD.md](DEMO_STORYBOARD.md), [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md), `docs/presentation/` | Slides without live evidence |

## Creativity — talking points

- Separates **commanded** (desired) vs **reported** (actual) profiles so telemetry `full` never “proves” `safe`.
- Recovery is evidence-based (continuous healthy samples), not a timer-only clear.
- Root cause explicitly contrasts thermal degradation with calm network metrics.

## Technical — talking points

- MongoDB is the control plane for detection and verification.
- Datadog is the operator plane for the same incident IDs.
- Repo-reproducible dashboard/monitor (not UI-only click-ops).

## Impact — talking points

- Observed on synthetic run `inc-thermal-edge-001-20261018085058`: GPU avg ~92°C → ~54°C; latency ~177ms → ~60ms; FPS ~12 → 18 after safe profile (see methodology file).
- Monitor ALERT → OK observed live.

## Presentation — talking points

- One incident story, one device (`edge-001`), one dashboard, one monitor.
- Explicitly narrate staged vs automatic when worker start is delayed for Alert visibility.
