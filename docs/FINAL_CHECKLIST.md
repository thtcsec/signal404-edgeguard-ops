# Final submission checklist

Baseline: `b0a5b35`. Update status as video/slides upload completes.

## Official expectations (from public MUGVN materials)

| Expectation | Status | Evidence |
| --- | --- | --- |
| Useful app solving an operational IoT/real-time problem | Done | Thermal edge-camera story |
| MongoDB time-series + TTL | Done | Ingest + `expireAfterSeconds` |
| Aggregation / window functions | Done | `$setWindowFields` analyzer |
| Datadog dashboard | Done (live) | Dashboard `9rr-a4u-2st` |
| Datadog monitor/alert | Done (live ALERT→OK) | Monitor `333934695` (demo) |
| Extra Datadog capability (logs and/or APM) | Done | Logs live; APM API service verified for ingest |
| End-to-end incident → recovery | Done | Incident RESOLVED / VERIFIED |
| Declare AI tools | Done | [AI_AND_REUSE_DISCLOSURE.md](AI_AND_REUSE_DISCLOSURE.md) |
| Declare pre-hackathon baseline | Done | [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md) |
| Demo video ≤ ~3 min | **Human** | [VIDEO_CAPTURE_CHECKLIST.md](VIDEO_CAPTURE_CHECKLIST.md) |
| Upload via official portal | **Human** | Confirm form fields on organizer site |

## Capability inventory

### Implemented + unit-tested

- [x] Ingest, commanded vs reported profile  
- [x] Thermal detection  
- [x] Remediation + continuous recovery (stall reset)  
- [x] .NET 9 + Python tests passing  

### Live Datadog observed

- [x] Metrics GPU / FPS / latency  
- [x] Structured logs  
- [x] Dashboard + demo monitor ALERT→OK  
- [x] APM service `edgeguard-telemetry-api`  
- [ ] APM services `edgeguard-health-analyzer` / `edgeguard-response-worker` in Datadog API — **NOT VERIFIED**  

### Staged vs automatic

- [x] Documented: delayed response-worker for Alert visibility ([DEMO.md](DEMO.md) B3, [IMPACT.md](IMPACT.md))  
- [x] Fully automatic poll path exists when all workers start together  

## Dependency advisories (NuGet audit)

| Package | Severity | Impact classification |
| --- | --- | --- |
| Datadog.Trace / Bundle 3.55.1 | Clean vs prior NU1903 | Patched |
| SharpCompress 0.30.1 (transitive via MongoDB stack) | Moderate | Not exercised as archive attack surface in this demo; track upstream MongoDB.Driver updates |
| Snappier 1.0.0 (transitive) | High advisory label | Compression helper transitive; no intentional untrusted-snappy surface in EdgeGuard paths; track upstream |

No secret materials in git. `.env` gitignored.

## Outstanding human actions

1. Record 3-minute demo video per checklist.  
2. Rehearse Vietnamese script once with live Agent + trial org.  
3. Optionally re-run APM with analyzer/worker enabled and screenshot services list.  
4. Submit portal package before **2026-10-31 23:59 ICT**.  
5. Confirm judging rubric weights if official PDF differs from internal 30/30/30/10 matrix.
