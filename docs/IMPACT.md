# Impact — EdgeGuard Ops

## Operational value (intended)

Factories running edge AI cameras lose inspection yield when GPU thermal throttling silently cuts FPS. EdgeGuard Ops shortens the path from “device looks slow” to “safe profile commanded and verified healthy,” with Datadog giving operators a shared timeline.

## What we measured (synthetic lab run — 2026-10-18)

Source incident: `inc-thermal-edge-001-20261018085058`  
Full methodology: [evidence/performance-metrics.json](evidence/performance-metrics.json)

| Metric | Value | Interpretation |
| --- | --- | --- |
| First telemetry → detection | **40.9 s** | From **first stored sample** to `incident.detectedAt` — **not** “seconds since anomaly onset” (heat ramps inside the simulator) |
| Detection → remediation request | **111.4 s** | **Includes intentional response-worker delay** for Datadog ALERT staging — **not** autonomous MTTA |
| Remediation request → VERIFIED | **18.2 s** | Observation window + continuous healthy reported-safe samples |
| Detection → RESOLVED | **~130 s** | End-to-end clock for this staged run |
| GPU temp (avg before detect → after resolve) | **92.3°C → 54.1°C** | Synthetic cooling under `safe` profile |
| Inference latency | **177.3 ms → 59.6 ms** | Same window methodology |
| FPS | **12.1 → 18.0** | **Safe-mode operating point** — demonstrates thermal headroom recovery, **not** a claim of full ~30 FPS restoration |
| Datadog monitor | **ALERT → OK** | Demo monitor `333934695` |
| APM (live verified) | **telemetry-api only** | Analyzer/worker share wiring; cloud service list not claimed for all three |

## What we do **not** claim

- Production fleet uptime, revenue, or camera counts.
- That 40.9 s is time from heat onset (it is first sample → detect).
- That 111.4 s detect→remediate is autonomous response latency.
- Full restoration to peak ~30 FPS after remediation.
- That network degradation or memory scenarios were live-validated in Datadog (code paths exist; thermal was the judged story).
- Live APM service visibility for analyzer and response-worker.

## Limitations affecting impact

- Synthetic data only (labeled on slides and in narration).
- Single-device demo path for judges (simulator supports multi-device).
- Polling-based workers (no change streams yet) — latency floor includes poll intervals.
- Staged Alert path delays worker start so judges can see ALERT; automatic E2E (all workers up) is documented separately in [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md).

## Measurable outcomes suitable for slides

1. Closed loop completed: OPEN → … → RESOLVED + VERIFIED.  
2. Operator signal: Datadog ALERT → OK (staged demo disclosed).  
3. Quantitative recovery deltas on GPU / latency / FPS from MongoDB evidence (synthetic, safe-mode trade-off explicit).
