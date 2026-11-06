# Judging evidence map

No predicted scores or ranking. Creativity / Technical / Impact / Presentation are the requested review perspectives; previously documented scoring weights should be reconfirmed against current organizer rules before use.

| Perspective | Defensible strength | Evidence | Remaining weakness |
| --- | --- | --- | --- |
| Creativity | Safe action followed by evidence-gated recovery; commanded vs reported state | RecoveryEvidence and worker source; automatic walkthrough | Rule-based thermal scenario, not novel ML |
| Technical | MongoDB time-series, TTL, window aggregation and action state; Datadog metrics/logs/monitor/API APM | Source, tests, E2E JSON; dated Datadog evidence | Single worker, no distributed lease; worker APM not cloud-verified |
| Impact | Closed loop restores thermal headroom at reduced throughput | Run 20261021202014: safe, 54.73°C / 18 FPS; 4.713 s request / 29.824 s resolve | Synthetic single run; no production ROI or scale benchmark |
| Presentation | Authentic 80.1 s captioned editorial walkthrough, current form text and Q&A | Video audit, editable current slide content | Hosted video and judge-readable access pending; dense terminal text needs fullscreen |

MongoDB provides persisted operational truth and recovery queries. Datadog provides operator investigation and visibility. Workers make the automated decisions. October 18 staged ALERT→OK is separate from the primary automatic October 21 E2E. See [walkthrough](submission/MUGVN2026_E2E_WALKTHROUGH.md) and [release report](submission/MUGVN2026_RELEASE_REPORT.md).
