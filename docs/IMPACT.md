# Impact — EdgeGuard Ops

## Operational value (intended)

Factories running edge AI cameras lose inspection yield when GPU thermal throttling silently cuts FPS. EdgeGuard Ops shortens the path from “device looks slow” to “safe profile commanded and verified healthy,” with Datadog giving operators a shared timeline.

## What we measured (synthetic lab run — 2026-10-18)

Source incident: `inc-thermal-edge-001-20261018085058`  
Full methodology: [evidence/performance-metrics.json](evidence/performance-metrics.json)

| Metric | Value | Interpretation |
| --- | --- | --- |
| First telemetry → detection | **~41 s** | Analyzer + window aggregation on 1s samples |
| Detection → remediation request | **~111 s** | **Includes intentional response-worker delay** for Datadog ALERT staging — **not** autonomous MTTA |
| Remediation request → VERIFIED | **~18 s** | Observation window + continuous healthy reported-safe samples |
| Detection → RESOLVED | **~130 s** | End-to-end clock for this staged run |
| GPU temp (avg before detect → after resolve) | **92.3°C → 54.1°C** | Synthetic cooling under `safe` profile |
| Inference latency | **177.3 ms → 59.6 ms** | Same window methodology |
| FPS | **12.1 → 18.0** | Same window methodology |
| Datadog monitor | **ALERT → OK** | Demo monitor `333934695` |

## What we do **not** claim

- Production fleet uptime, revenue, or camera counts.
- That the ~111 s detect→remediate interval is the system’s best autonomous response time.
- That network degradation or memory scenarios were live-validated in Datadog (code paths exist in the simulator; thermal was the judged story).

## Limitations affecting impact

- Synthetic data only.
- Single-device demo path for judges (simulator supports multi-device).
- Polling-based workers (no change streams yet) — acceptable for demo scale; latency floor includes poll intervals.

## Measurable outcomes suitable for slides

1. Closed loop completed: OPEN → … → RESOLVED + VERIFIED.  
2. Operator signal: Datadog ALERT → OK.  
3. Quantitative recovery deltas on GPU / latency / FPS from MongoDB evidence (synthetic).
