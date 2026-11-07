# Claim audit — November 6, 2026

Baseline: local main `639c83a` plus pre-existing dirty editorial/video work. Local origin/main matched that commit; no network freshness implied. Source and raw evidence take precedence over old reports.

| Claim | Source evidence | Current validity | Required correction / outcome |
| --- | --- | --- | --- |
| Deadline October 31 | Official form read-only HTTP 200 November 6 | Obsolete | Current README/submission/checklist use November 8, 23:59 ICT |
| API HTTP 501, simulator exits, workers idle | Program.cs, simulator main, worker/analyzer source | False for current code | Architecture rewritten; September baseline preserved |
| No collections created | EdgeGuardMongoContext | False | Data-model introduction/bootstrap/index language corrected |
| Change streams drive response | RemediationWorker / executor | False | Current architecture says polling |
| Automatic E2E only planned | E2E 20261021202014 + simulator and process logs | Obsolete | Primary current evidence is completed automatic run |
| 4.7 s request / 29.8 s resolved | Raw detectedAt/requestedAt/resolvedAt | Valid for one synthetic run | Exact computed 4.713 / 29.824 s, no benchmark claim |
| Safe-mode 18 FPS means failure | ThermalThrottleScenario safe branch + snapshot | False | Reduced throughput is intended; no full-FPS restoration claim |
| Datadog triggers remediation | Worker code, monitors definitions | False | Workers own decisions, Datadog operator view |
| October 18 ALERT→OK is October 21 automatic evidence | live-datadog-validation and separate run IDs | Unsupported | Explicitly separated across current documents |
| Live “now” widgets prove recovered historic values | Capture metadata and video overlay | False | Historical graphs/logs vs live widgets distinguished; MongoDB supplies final sample |
| 54.73°C is all post-recovery averages/video sample | E2E latest_telemetry, video Mongo query | False | Label as single captured sample; video later query differs |
| All three APM services verified | Dated Datadog services evidence | Unsupported | Cloud verification limited to telemetry-api |
| Five-minute baseline measured during short E2E | Analyzer log equal 1/5-minute averages | False | Absolute threshold path explained |
| Command alone resolves | RecoveryEvidence + executor | False | Continuous evidence verified; failure ordering hardened |
| No duplicate actions under partial failure | Old timestamp action ID and last incident-link write | False before hardening | Stable per-incident ID and duplicate insert preservation; targeted restart test |
| Failed action verification cannot leave success | Old incident-before-action write | False before hardening | Verify action before resolving; missing/mismatched action remains unresolved |
| Future telemetry proves elapsed recovery | Old evaluator accepted future samples | Unsafe | Future samples reset evidence; regression test |
| Final video is 90.1 s / voiceover | Actual ffprobe, AAC volume and sampled frames | Obsolete | Preserve existing dirty 80.1 s manifest; add independent checksum/audit |
| Private repository accessible to judges | Authenticated gh visibility; anonymous 404 | Not established | Human access setup required, no visibility change |
| No secrets in all materials | Bounded tracked-text scan + sampled visual evidence | Only partial coverage | Zero pattern hits; no full-history/OCR/entropy guarantee |
| Scoring weights/access-through-Nov22 official confirmed now | Prior repository statements only | Not independently verified here | Remove current scoring assertion; access retention reconfirmation noted |

Historical baseline, E2E JSON, old QA reports and original staged measurements remain intact. A new editable eight-slide submission PPTX preserves the original deck and separates automatic-run talking points from the historical staged slide.

## November 7 reconciliation

The prior private-repository finding above is a November 6 observation. Current metadata and unsigned HTTP show PUBLIC visibility; remote main remains 639c83a, and the hardening branch/40ee9ee URLs return 404. See [current GitHub audit](MUGVN2026_GITHUB_AUDIT.md). The local 80.1-second SRT/manifest were previously uncommitted; the original video bytes remain unchanged.
