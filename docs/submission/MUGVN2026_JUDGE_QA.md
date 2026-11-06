# Judge Q&A — Signal404 / EdgeGuard Ops

**Why not just use a Datadog monitor?** A monitor tells an operator that a metric crossed a threshold. EdgeGuard additionally commands a safe profile, separates commanded and reported state, persists incident/action linkage, and waits for recovery evidence. The application workers own that loop; Datadog supplies the operator timeline and investigation tools.

**Why MongoDB rather than only metrics?** MongoDB stores individual device samples with metadata and retention, runs `$setWindowFields` analytics, and persists mutable device/incident/action state. Recovery queries use reported profile, health and sample timing together. Datadog's aggregated metrics remain valuable for fleet visibility, while MongoDB holds the operational records.

**How do you prevent false recovery?** A command is intent. The worker waits for continuous reported-safe, healthy telemetry with temperature, latency and FPS limits, minimum sample count, a completed observation window, fresh latest sample and bounded gaps. Future-dated samples are rejected as evidence. November hardening also requires a matching persisted action to be VERIFIED before RESOLVED is written. These are lab safeguards, not authenticated proof of physical-device state.

**What if telemetry stops?** Missing/stale/gapped recovery samples reset the observation clock and cannot resolve the incident. The worker logs the reason. A restart starts a new in-memory observation period. There is no separate implemented fleet-offline incident workflow or guaranteed escalation deadline.

**Why 18 FPS instead of 29 FPS?** Safe mode deliberately reduces synthetic inference workload. The thermal scenario clamps its safe-mode result to at least 18 FPS; it yields cooling and lower latency at reduced throughput. We do not claim restoration to full processing performance or a validated physical thermal model.

**What is synthetic and what is live?** Device telemetry and cooling are synthetic Python scenario outputs. The HTTP API, MongoDB database operations, .NET workers and recorded Datadog cloud dashboard/logs are real. The final 80.1 s video is an editorial cut with time compression, a replay of corroborated worker-log messages, and held MongoDB frames. No camera hardware or custom frontend is shown.

**What is innovative compared with monitoring?** The combination of thermal-vs-network rules, explicit commanded-vs-reported state, automatic safe action and evidence-gated resolution closes the operator workflow. It is application engineering, not novel ML or an AI runtime agent.

**How is thermal distinguished from network failure?** The analyzer combines hot/rising GPU with high inference latency or low FPS and checks packet loss/network latency are calm. In the primary short startup run, 1/5-minute averages are equal and absolute thresholds trigger detection. We do not claim full cause identification or remediation for all simulated scenario types.

**What was actually measured?** Automatic run `20261021202014`: detection→request 4.713 s; detection→resolved 29.824 s. Captured final sample: safe/healthy, 54.73°C, 18 FPS, 60.9 ms. One synthetic run, not a latency distribution. The October 18 ALERT→OK used delayed worker start and is separate.

**How do retries work?** New actions use a stable ID per incident. A sequential retry after a partial failure reuses the stored action rather than creating another. Failed action verification leaves the incident RECOVERING. Historical IDs are preserved. This does not provide multi-worker leasing or cross-document transactions; one analyzer and one response worker are the supported topology.

**Which APM services are verified?** `edgeguard-telemetry-api` only in the dated cloud evidence. Analyzer/worker have instrumentation wiring and local trace IDs, but that is not cloud verification of both services or a single propagated distributed trace.

**How would a real fleet evolve?** Add authenticated device identity and TLS, reliable command acknowledgements, validated clock/sequence handling, durable recovery state, distributed claims/leases, bounded retries/escalation and audit policy. Validate real camera safe profiles, staged rollout and rollback, retention/cost controls, high-cardinality metric strategy, multi-tenant isolation and load behavior. These are future requirements, not current features.

**Remaining production limits?** Synthetic-only validation; unauthenticated lab API and self-managed local MongoDB; single-worker topology; no fleet-scale benchmark, high availability, hard command safety envelope, transactional terminal-state update or durable observation clock. NuGet audit still reports transitive SharpCompress/Snappier advisories; see release report. The private repository and hosted-video access must be completed before submission.

**How can judges review it?** Start with README, the automatic walkthrough, source and tests, then replay the captioned video. Use the non-destructive local instructions with a new database. Datadog cloud UI requires org access; provide genuine accessible captures rather than judge credentials. No login secrets belong in the form.
