# Final submission checklist

Deck / docs baseline after judge-deck revamp — update SHA after commit. Do **not** delete existing `docs/evidence/*`.

## Official expectations (from public MUGVN materials)

| Expectation | Status | Evidence |
| --- | --- | --- |
| Useful app solving an operational IoT/real-time problem | Done | Thermal edge-camera story |
| MongoDB time-series + TTL | Done | Ingest + `expireAfterSeconds` |
| Aggregation / window functions | Done | `$setWindowFields` analyzer |
| Datadog dashboard | Done (live) | Dashboard `9rr-a4u-2st` |
| Datadog monitor/alert | Done (live ALERT→OK) | Monitor `333934695` (demo) |
| Extra Datadog capability (logs and/or APM) | Done | Logs live; APM **telemetry-api** verified |
| End-to-end incident → recovery | Done | Incident RESOLVED / VERIFIED |
| Declare AI tools | Done | [AI_AND_REUSE_DISCLOSURE.md](AI_AND_REUSE_DISCLOSURE.md) |
| Declare pre-hackathon baseline | Done | [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md) |
| Demo video (confirm duration on form) | **Human** | [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md), [VIDEO_CAPTURE_CHECKLIST.md](VIDEO_CAPTURE_CHECKLIST.md) |
| Upload via official portal | **Human** | Confirm final form fields on organizer site |
| Finals scoring weights | Confirmed public | Creativity 30% · Technical 30% · Impact 30% · Presentation 10% |

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
- [ ] APM services `edgeguard-health-analyzer` / `edgeguard-response-worker` in Datadog — **NOT VERIFIED**  

### Staged vs automatic

- [x] Documented: delayed response-worker for Alert visibility  
- [x] Automatic E2E plan when all workers already running — [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md) §B  

### Presentation

- [x] Editable 8-slide PPTX regenerated (visual architecture, metric bars, corrected claims)  
- [x] No fabricated Datadog screenshots (login required; optional real PNGs supported)  

## Dependency advisories (NuGet audit)

| Package | Severity | Impact classification |
| --- | --- | --- |
| Datadog.Trace / Bundle 3.55.1 | Clean vs prior NU1903 | Patched |
| SharpCompress 0.30.1 (transitive via MongoDB stack) | Moderate | Track upstream MongoDB.Driver |
| Snappier 1.0.0 (transitive) | High advisory label | Track upstream; no intentional untrusted-snappy surface |

No secret materials in git. `.env` gitignored.

## Mandatory human actions (organizer compliance)

1. **Confirm the final submission form** on the official site and any **video-duration restrictions** (target ≤3:00 unless form says otherwise).  
2. **Provide judge read access** to the private repository using the **accounts supplied by organizers**.  
3. **Maintain repository access through November 22, 2026.**  
4. **Complete submission before October 31, 2026, 23:59 ICT.**  
5. **Do not modify the repository after the deadline.**  
6. Record the demo video per [RECORDING_SEQUENCE.md](RECORDING_SEQUENCE.md) (one explicit staged-Alert disclosure).  
7. Rehearse [DEMO_SCRIPT_VI.md](DEMO_SCRIPT_VI.md) once with live Agent + trial org.  
8. Optionally capture authentic Datadog PNGs into `docs/presentation/assets/` and regenerate the deck — never invent screenshots.

## Claim hygiene (do not regress)

- 40.9s = first stored sample → detect (not anomaly-onset clock).  
- 111.4s includes intentional worker delay ≠ autonomous MTTA.  
- FPS 12.1→18.0 = safe-mode recovery ≠ full ~30 FPS.  
- APM live claim = telemetry-api only.  
- All demo telemetry labeled synthetic.
