# Final release validation — November 6, 2026

**November 7 access update:** repository visibility is now PUBLIC and anonymous HTTP returns 200. Older private/access findings below describe November 6, not current visibility. The audited branch and final validation artifacts remain local until approved publication; see [current GitHub audit](MUGVN2026_GITHUB_AUDIT.md). No visibility change was made by this audit.

## Decision: NO-GO for submission; technical validation GO

Verified product commit: **`40ee9ee58f3a638f364850db2b5ab647b0d6b482`**. A clean detached checkout at `D:/tu_projects/eg-release-40ee9ee` supplied all application binaries, tests and simulator. No product source was changed. The original branch remains at `40ee9ee`; this validation adds only local documentation, provenance and evidence. No push, merge, deploy, access change, video rebuild or form submission occurred.

The runtime blocker is closed. Overall submission remains **NO-GO** until the audited release is published to the public repository, the exact video is hosted with permission-free playback, and judge-readable architecture/dashboard evidence URLs are verified. The repository is already public (November 7); unpublished local commits and Datadog login walls remain blockers. No new live Datadog validation was performed.

## Docker diagnosis and recovery

Initial state: Docker Engine pipe unavailable; Docker Desktop backend had aborted before starting the WSL engine. WSLService was running and Ubuntu WSL2 was healthy; docker-desktop was stopped. `com.docker.service` was stopped/manual, but remains stopped while the restored WSL engine works, so this was not the demonstrated blocker.

Docker host logs identified inaccessible stale Unix-domain socket reparse points, first `Docker/run/dockerInference`, then `docker-secrets-engine/engine.sock`. Files were zero-byte reparse points; both `fsutil` inspection and direct socket rename returned Windows error 1920. Graceful Desktop stop timed out. The failed Desktop/backend processes were stopped, and socket-only **parent directories** were renamed to preserve their contents. No data, credential store contents, WSL disk or volumes were removed. An intermediate restart recreated one endpoint before failing at the second; restarting with both endpoint directories fresh succeeded.

Preserved endpoint directories:

- `%LOCALAPPDATA%/Docker/run.pre-release-20261106`
- `%LOCALAPPDATA%/Docker/run.pre-release-attempt2-20261106`
- `%LOCALAPPDATA%/docker-secrets-engine.pre-release-20261106`

This establishes the immediate startup failure and a successful recovery; why the stale endpoints became inaccessible is **not established**. No Docker reset, reinstall, global WSL shutdown, credential rotation, or data-volume deletion was performed. Official troubleshooting context: [Docker Desktop troubleshooting](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/).

Original `edgeguard-ops-mongodb-1` remains stopped with exit code 0. Compose logs show clean shutdown on October 21; no new original Mongo startup/crash was observed. Its `edgeguard-ops_edgeguard_mongo` volume was not mounted by validation. Restoring Docker exposed the existing containers/volumes intact; no original application container was started.

Isolated project `edgeguard-release-validation` runs MongoDB **8.3.13**, image `sha256:0e900a3364da37b76d642b73b0bba56bd4c6c509ab470cf700436fd866bee3ff`, at **127.0.0.1:27027**. Both `/data/db` and `/data/configdb` are tmpfs; no existing volume mount. Resource limits: 1 CPU / 768 MB. Docker Engine 29.6.2, WSL 2.7.3. The repo's mutable `mongo:8` tag resolved to this cached image; results are not claimed for every MongoDB 8 minor version.

The isolated container is left healthy for review. Fixture data is temporary and will disappear when that container stops; exported JSON/logs/TRX below preserve the evidence. API, analyzer, response worker and simulator launched for E2E were stopped by the harness after export. Other projects and Ubuntu WSL were not stopped or reset.

## Exact verification results

| Check | Passed | Failed | Not run | Evidence |
| --- | ---: | ---: | ---: | --- |
| .NET suite, Release | 15 | 0 | 0 | Full TRX; includes all four Mongo-backed tests |
| Of those: Mongo-backed API tests | 4 | 0 | 0 | Health, valid ingestion, commanded-safe preservation, invalid-device rejection |
| Of those: existing focused tests | 11 | 0 | 0 | Recovery, contracts and retry/failure/order tests |
| Python simulator tests | 6 | 0 | 0 | pytest; existing asyncio configuration warning only |
| Additional real-Mongo fault/retry checks | 16 | 0 | 0 | Separate scratch harness, not counted as new committed tests |
| Complete automatic synthetic E2E | 1 | 0 | 0 | Default 20-second observation; workers prestarted |
| Release build | PASS | 0 errors | — | .NET SDK 9.0.318; 0 warnings |
| Original + isolated Compose config | PASS | 0 | — | `config --quiet`; isolated startup health passed |
| New live Datadog/APM/monitor exercise | — | — | NOT RUN | Datadog disabled; no new cloud verification claimed |
| Hosted video / judge access / form submission | — | — | NOT RUN | Requires authorized human actions |

Commands from detached checkout:

```powershell
& "$env:USERPROFILE/.dotnet/dotnet.exe" restore EdgeGuardOps.sln
& "$env:USERPROFILE/.dotnet/dotnet.exe" build EdgeGuardOps.sln --no-restore -c Release
$env:EDGEGUARD_TEST_MONGODB = "mongodb://127.0.0.1:27027"
& "$env:USERPROFILE/.dotnet/dotnet.exe" test EdgeGuardOps.sln --no-build --no-restore -c Release --logger "trx;LogFileName=full-suite.trx"
python -m pytest apps/device-simulator -q
```

All four tests used the existing random `edgeguard_test_*` database fixture, now connected to the isolated server. The fixture only cleans its own generated databases. No production/evidence reset scripts were used.

## Automatic E2E on 40ee9ee

Validation run **`20261106225132`** identifies this validation session, not the simulator start clock. Actual process/sample timestamps are exported. All event times below are **UTC on November 6**; ICT = UTC+7.

- Incident: `inc-thermal-edge-001-20261106155734`
- Action: `act-safe-inc-thermal-edge-001-20261106155734`
- Detection: **15:57:34.959**
- Request: **15:57:39.920**; APPLIED log **15:57:39.9722416**
- RECOVERING log: **15:57:45.0046220**, observation **20 s**
- VERIFIED action `completedAt`: **15:58:05.097**
- RESOLVED incident `resolvedAt`: **15:58:05.098**
- Captured latest safe/healthy sample: **15:58:06.649**, **52.99°C / 18 FPS / 58.3 ms**

Default analyzer and remediation settings were used. API ran at loopback port 5088; all services used a new `edgeguard_release_20261106225132` database. Workers were running before the thermal simulator started. The event series captured healthy/full → degraded/full → OPEN → APPLIED with commanded safe while reported full → reported safe → RECOVERING → RESOLVED/VERIFIED.

The exported final 20-second sample window contains continuous healthy reported-safe evidence, GPU ≤75°C, latency ≤80 ms, FPS ≥18, enough samples spanning at least 15 seconds, bounded inter-sample gaps ≤5 seconds and latest age at resolution ≤5 seconds. The worker's 20-second observation completed; issuing a safe command alone did not resolve the incident. No premature resolution was observed in 250 ms polling, and the code's action-before-resolution order is additionally exercised by injected failure checks.

Detection→request **4.961 s**; detection→resolution **30.139 s**. These are a new **single-run synthetic observation**, not a production benchmark. The short startup uses the absolute thermal threshold, not a filled five-minute baseline. Datadog is disabled in this run; it validates the core control loop, not current cloud ingestion.

## Explicit idempotency / no-premature-resolution checks

A separate C# harness references the unchanged 40ee9ee projects and uses real Mongo repositories with injected exceptions immediately before selected writes. It uses its own new `edgeguard_retry_*` fixture database and a **2-second test-only observation override**; this must not be confused with the default 20-second automatic E2E.

The 16 passing assertions cover: action persisted after failed incident-link write; incident remains OPEN; restart after >1 second retains exactly one action; ID/requestedAt preserved; incident links the original action; duplicate insert does not overwrite stored action; same ID with mismatched incident is rejected; command without telemetry does not resolve; reported full does not resolve; reported safe enters RECOVERING; incomplete window stays RECOVERING; failed verification write keeps incident RECOVERING and action APPLIED; retry with healthy evidence reaches RESOLVED/VERIFIED; VERIFIED timestamp precedes RESOLVED; terminal reprocessing creates no additional action.

These validate sequential retry idempotency and safe failure handling with the real persistence implementation. They do not establish multi-worker exactly-once semantics, transactions, durable recovery clocks or production-device trust.

## Release reconciliation and security

The original dirty files were fingerprinted before validation. Product source and detached checkout remain unchanged; no staged changes were present. Pre-existing editorial report, subtitles, preview changes/deletions, builder edits and untracked recordings remain preserved. The manifest's existing fields are preserved; only a separate November validation provenance object is added. Current README, architecture, submission overview and checklist point here. The earlier release report is retained as the superseded initial-pass record rather than silently converting its earlier failures into passes.

**The original video does not record HEAD 40ee9ee.** It remains the October 21 execution `20261021202014`, with its historical IDs and editorial replay caveats. No video was rebuilt, recaptured, or replaced. Current manifest duration **80.1 seconds**; independent ffprobe **80.100000 s**, 1920×1080 H.264 at 30 fps, AAC; 5,458,614 bytes. Original and final SHA-256 match:

`deb7e1ababa4826dc5470ba098aa9537f043449713d5dfc11043bcebe673d348`

The 90-second backup is unchanged. The new November E2E is separately exported and was **not recorded on video**. Historical October E2E/monitor evidence is not relabeled as validation of this commit.

Bounded scan: **197 text/PPTX-XML/UTF16-log files**, no credential-pattern matches; **179 binary files not OCR-scanned**. `.env` and MP4 remain ignored and untracked. No full-history/entropy/OCR clearance is claimed. Fresh dependency audit still reports **SharpCompress 0.30.1 Moderate** and **Snappier 1.0.0 High**. No dependency migration or new feature was introduced. Lab authentication/single-worker/production-safety limitations in existing docs remain applicable.

## Evidence and remaining actions

Portable summary and snapshots: [final-release-validation-20261106225132.json](../evidence/final-release-validation-20261106225132.json). This includes commit identity, exact test counts, all 16 Mongo checks, automatic chronology, final state, recovery sample window, corroborating worker messages, video provenance and DLL hashes.

Local detailed artifacts: `artifacts/release-validation-20261106225132/` — full-suite TRX, E2E harness and logs, full telemetry export, Mongo fault harness/results, Compose definition/logs, scan/advisory results, original manifest and preservation hashes. The detached worktree remains available for reproduction; neither it nor the scratch harness changes the reviewed commit.

Before submission: approve push of the reviewed package, supply verified judge-readable repository/architecture/dashboard evidence URLs, host the exact MP4 and verify access/playback, replace form placeholders, enter registered personal details and attest/submit before **November 8, 2026, 23:59 ICT**. No such external actions have been performed.
