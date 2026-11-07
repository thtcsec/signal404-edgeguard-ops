# EdgeGuard Ops — final submission overview

**Team:** Signal404 · **Deadline:** November 8, 2026, 23:59 ICT. Confirmed read-only on the [official form](https://docs.google.com/forms/d/e/1FAIpQLSd31MPvuUw_e2fZQFmMd-m_RrGyVSJJte_-5ctpAu_LRYap5A/viewform), November 6.

**Monitoring detects the problem. EdgeGuard acts on it and verifies recovery.**

Edge AI camera thermal throttling can resemble a network problem. EdgeGuard combines GPU/latency/FPS and calm-network telemetry, commands safe mode automatically, and requires fresh, continuous healthy reported-safe telemetry before declaring recovery.

The [automatic walkthrough](submission/MUGVN2026_E2E_WALKTHROUGH.md) anchors the submission in run `20261021202014`: RESOLVED / VERIFIED / safe, with a captured 54.73°C / 18 FPS sample. Single-run synthetic detection→request 4.713 s and detection→resolved 29.824 s are observations, not production performance guarantees. Safe mode deliberately reduces throughput.

MongoDB 8 is the self-managed operational store: time-series + 14-day default TTL, per-device window aggregation, devices, incidents, actions and recovery queries. Datadog supplies metrics, dashboard, structured investigation logs, monitor definitions and cloud-verified telemetry-api APM. Application workers perform detection and remediation; Datadog does not trigger this control loop. See [architecture](ARCHITECTURE.md) and [observability](OBSERVABILITY.md).

Evidence sets remain distinct:

- October 18 staged demo: delayed worker start for monitor ALERT→OK; 111.4 s includes that delay. [Historical measurements](evidence/performance-metrics.json).
- October 21 automatic run `20261021183352`: separate preserved execution.
- October 21 automatic run `20261021202014`: primary recorded E2E, paused Datadog historical graphs and ID-correlated logs. No monitor transition claimed for this run.

## Current release validation

Commit `40ee9ee` passed all 15 .NET tests, 6 Python tests, 16 additional Mongo retry/failure assertions and a separate November 6 automatic E2E. [Exact results and release decision](submission/MUGVN2026_RELEASE_VALIDATION.md). Runtime blocker closed; submission remains NO-GO pending required hosted URLs and judge access. The October video and timings above remain historical and do not record this commit.

## Review package

- [Exact form content](submission/MUGVN2026_FORM_CONTENT.md)
- [Final checklist](submission/MUGVN2026_FINAL_SUBMISSION_CHECKLIST.md)
- [Judge Q&A](submission/MUGVN2026_JUDGE_QA.md)
- [Release report and verification](submission/MUGVN2026_RELEASE_REPORT.md)
- [Current editable PPTX](presentation/EdgeGuard-Ops-Submission-20261106.pptx)
- [Current editable slide content](presentation/SLIDES.md)
- [Final video audit](submission/MUGVN2026_VIDEO_AUDIT.md)
- [Non-destructive run instructions](../README.md#run-locally)

Repository: [thtcsec/signal404-edgeguard-ops](https://github.com/thtcsec/signal404-edgeguard-ops), **PUBLIC**, confirmed by authenticated metadata and unsigned HTTP 200 on November 7. Remote `main` still serves `639c83a`; the audited hardening release is local until explicitly authorized publication. Public visibility alone does not publish a local commit. Demo: `[HOSTED_VIDEO_URL_PENDING]`. Use the [current link audit](submission/MUGVN2026_GITHUB_AUDIT.md) to distinguish accessible historical URLs from correct release artifacts. Do not submit placeholders.

## Limits and disclosure

Synthetic telemetry only, no physical camera integration, no production ROI, no fleet-scale latency benchmark, no propagated end-to-end distributed trace. Cloud APM verified for telemetry-api only. Supported topology is one analyzer and one response worker; no distributed exactly-once guarantee. No public unauthenticated deployment is intended.

Pre-window scaffold and original October build dates remain in [historical baseline](PRE_HACKATHON_BASELINE.md). [AI/reuse disclosure](AI_AND_REUSE_DISCLOSURE.md) includes this November hardening pass. Maintain access for judges through November 22 as recorded in prior team compliance notes; reconfirm organizer account list and retention instructions. Technical evaluation November 9–12, Top 8 November 13, online final November 15 are team-supplied organizer-email dates; this review found no matching email in the connected mailbox.
