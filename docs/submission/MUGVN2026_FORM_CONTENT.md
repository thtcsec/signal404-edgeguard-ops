# Official form — prepared content (not submitted)

Read-only GET of the [official form](https://docs.google.com/forms/d/e/1FAIpQLSd31MPvuUw_e2fZQFmMd-m_RrGyVSJJte_-5ctpAu_LRYap5A/viewform) returned HTTP 200 on November 6, 2026. Labels, required flags and sections below come from its embedded public form data, including later pages. No answers were transmitted. The form permits English or Vietnamese. Deadline: November 8, 23:59 ICT.

**Replace placeholders, publish only with explicit approval, and verify judge access before entering URLs.** Registered personal details remain human inputs.

## Phần A — Thông tin đội

### Tên đội (như lúc đăng ký) (required)

Signal404

### Họ tên trưởng đội (required)

[TEAM LEADER: registered full name — fill personally]

### Email trưởng đội (email đã đăng ký) (required)

[TEAM LEADER: registered email — fill personally]

### Thành viên khác trong đội (optional)

[Confirm registered members; leave blank if solo]

## Phần B — Tổng quan dự án

### Tên dự án (required)

EdgeGuard Ops

### Lĩnh vực chính (optional)

IoT / Telemetry thiết bị

### Bài toán và người dùng (required)

Edge AI camera and inference fleets can lose processing capacity when GPU thermal throttling raises latency and drops FPS while network metrics remain calm. Operators need a safe response and proof of recovery, not only an alert. The intended users are operators of industrial edge-camera fleets; validation here uses synthetic telemetry, not a production deployment.

### Giải pháp và tính năng chính (required)

Monitoring detects the problem. EdgeGuard acts on it and verifies recovery. A Python simulator posts synthetic device telemetry to an ASP.NET Core 9 API. A MongoDB-backed analyzer detects a thermal pattern; a polling response worker commands safe mode and waits for fresh, continuous healthy reported-safe telemetry. Datadog displays metrics and ID-correlated investigation logs. Recorded automatic run 20261021202014 reached RESOLVED / VERIFIED with device safe and a captured 54.73°C / 18 FPS sample. Safe mode sacrifices peak throughput for thermal headroom.

### Điểm sáng tạo hoặc thách thức kỹ thuật (optional)

The closed loop separates commanded device state from reported evidence. Merely issuing safe mode cannot resolve an incident; missing/stale/gapped telemetry resets recovery observation. Sequential retries reuse an action per incident, and action verification must persist before resolution. Thermal-versus-network rules, MongoDB window analytics and Datadog investigation make the operational reasoning inspectable. One analyzer/worker is the supported topology; distributed exactly-once execution is not claimed.

## Phần C — Kiến trúc và MongoDB

### Link sơ đồ kiến trúc (required)

[REQUIRED JUDGE-READABLE HTTPS URL — candidate after approved publication: https://github.com/thtcsec/signal404-edgeguard-ops/blob/mugvn2026/submission-hardening/docs/ARCHITECTURE.md ; not currently published/access-verified]

### Mô tả kiến trúc và luồng dữ liệu (optional)

Python simulator → HTTP telemetry API → MongoDB time-series. Health Analyzer polls MongoDB and uses per-device $setWindowFields aggregation to create an incident. Response Worker polls active incidents, records an action, sets devices.profile=safe, then evaluates reported telemetry to verify recovery. Simulator retrieves commanded profile through the API. DogStatsD and structured file logs flow through Datadog Agent to the cloud dashboard; telemetry-api APM was verified. No Kafka, Kubernetes, change streams, physical camera or custom frontend is required.

### Triển khai MongoDB (required)

Self-managed MongoDB 8 via local Docker Compose. telemetry is a time-series collection with timestamp time field, metadata grouping field, seconds granularity and default 14-day TTL. devices, incidents and remediation_actions hold operational state; status/detection and device/detection indexes support queries. $setWindowFields computes trailing 1/5-minute temperature, latency and FPS windows with network checks. Recovery queries enforce reported profile, health, freshness and continuity. Commands use field updates to preserve commanded state. No Atlas or change-stream usage is claimed.

## Phần D — Datadog và tình huống vận hành

### Triển khai Datadog (required)

Datadog Agent receives DogStatsD device/incident/action metrics and structured JSON file-tail logs. Reproducible dashboard and separate demo/production monitor definitions are versioned. Dated live evidence verifies metrics/logs, a staged October 18 monitor ALERT→OK and telemetry-api APM. The October 21 automatic E2E uses paused historical graphs plus correlated incident logs; it does not claim the same monitor transition. Application workers, not Datadog monitors, execute the automated response. Analyzer/worker cloud APM is not verified.

### Kịch bản sự cố: Phát hiện → Điều tra → Xử lý (required)

Automatic synthetic run 20261021202014 began healthy/full. Thermal degradation occurred while packet loss and network latency were calm. Incident inc-thermal-edge-001-20261021132057 was detected at 2026-10-21T13:20:57.469Z. Action act-safe-edge-001-20261021132102 was requested at 13:21:02.182Z; worker logs show safe command APPLIED, then RECOVERING at 13:21:07.2129666Z. Continuous healthy reported-safe evidence led to RESOLVED at 13:21:27.293Z and VERIFIED completedAt 13:21:27.297Z in that historical run. Final captured sample at 13:21:30.432Z: safe, healthy, 54.73°C, 18 FPS, 60.9 ms. Current hardening writes VERIFIED before RESOLVED to prevent partial-write false success; original evidence is unchanged.

### Link dashboard Datadog hoặc ảnh chụp màn hình (required)

Preferred after approved release publication: https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/mugvn2026/submission-hardening/docs/submission/assets/datadog-oct21-captioned-video-frame.png — candidate only, not yet remotely available.

Existing anonymously accessible historical screenshot: https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/main/docs/video/recordings/still-dashboard.png (HTTP 200; bytes match local capture). It shows the October 21 paused window and correlated log; lower GPU-now/FPS-now widgets are capture-time live values, not recovered telemetry. Prefer the captioned video-frame crop with that distinction visible after publication. Datadog org dashboard https://app.datadoghq.com/dashboard/9rr-a4u-2st redirects anonymous users to login.

### Kết quả đo được (optional)

Single automatic synthetic run: detection→remediation requested 4.713 seconds; detection→incident resolved 29.824 seconds. Captured final reported-safe sample: 54.73°C / 18 FPS / 60.9 ms. These are timestamp-derived observations from one run, not production latency benchmarks or measured ROI. 18 FPS is the intended safe-mode operating point, not restoration to full ~29 FPS. October 18 staged monitor ALERT→OK is separate evidence.

### Yêu cầu kỹ thuật tối thiểu đã đáp ứng (optional)

Suggested selections after team evidence review: all five listed capabilities — MongoDB operational backend; Aggregation Pipeline; Datadog dashboard; monitor/alert; additional Logs and API APM. This document does not tick or submit them.

## Phần E — Mã nguồn, tài liệu và demo

### Link repository mã nguồn (required)

https://github.com/thtcsec/signal404-edgeguard-ops — PUBLIC and anonymously accessible on November 7. It currently shows older main (639c83a). Publish the audited release only after explicit approval, then verify the exact branch/commit before submitting.

### Link README / hướng dẫn cài đặt (required)

[After authorized push and artifact verification] https://github.com/thtcsec/signal404-edgeguard-ops/blob/mugvn2026/submission-hardening/README.md — candidate only; branch is local now.

### Link video demo (required)

[HOSTED_VIDEO_URL_PENDING — upload exact 80.1-second checksummed local MP4, then verify judge access]

### Link slide thuyết trình (optional)

[After approved publication] https://github.com/thtcsec/signal404-edgeguard-ops/blob/mugvn2026/submission-hardening/docs/presentation/EdgeGuard-Ops-Submission-20261106.pptx — candidate only; updated editable deck is local and not yet remotely accessible.

### Link demo trực tiếp (optional)

Leave blank. No public hosted application is provided; local reproduction instructions are in README.

### Khai báo thành phần tái sử dụng, dataset và công cụ AI (required)

The September 30 pre-hackathon scaffold included layout, contracts/DTOs, configuration and placeholder services, drafted with Cursor. Functional detection/remediation/recovery and Datadog wiring were developed in the original October build period. Cursor and ChatGPT assisted implementation/review; Codex assisted the November 6 source/evidence audit, targeted fixes/tests and submission hardening. Third-party components include .NET/ASP.NET Core, MongoDB.Driver, Datadog.Trace.Bundle, DogStatsD client, Python/pytest and Docker/Datadog Agent. Telemetry is generated synthetically; no external customer dataset or production camera feed is used. See AI_AND_REUSE_DISCLOSURE.md and PRE_HACKATHON_BASELINE.md for details.

### Hạn chế và hướng phát triển (optional)

Synthetic-only validation, single analyzer/worker topology, no distributed leases or cross-document transaction, in-memory recovery clock, no device authentication or production safety validation, no fleet-scale/ROI benchmark. Remaining transitive package advisories are documented. Future fleet work requires authenticated TLS device transport, reliable acknowledgements, durable state, leases/escalation, validated hardware-safe profiles, staged rollout and scale/cost testing.

## Phần F — Xác nhận

### Xác nhận của đội (required)

HUMAN ONLY: leader must read and confirm all four statements after reviewing correctness, competition terms, absence of secrets and judge access. No attestation has been made by this task.

### Ghi chú cho giám khảo (optional)

Please start with README → automatic run walkthrough → source/tests → captioned 80.1-second video. All device telemetry is synthetic. The October 18 staged monitor ALERT→OK and October 21 automatic run are distinct. The video compresses time, replays corroborated worker-log messages and holds MongoDB frames; paused historical graphs must not be read as live query-value widgets. Only telemetry-api APM is cloud-verified. Review uses a new database; do not run the legacy collection-reset recording scripts against preserved data.
