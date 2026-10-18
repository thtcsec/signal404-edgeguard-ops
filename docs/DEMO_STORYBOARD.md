# 3-minute demo storyboard

Goal: a judge understands problem → MongoDB+Datadog loop → autonomous remediation → verified recovery within 180 seconds.

**Staging note:** For Datadog ALERT visibility, start API + analyzer + simulator first; start **response-worker after** the demo monitor Alerts. Say this aloud once so judges do not confuse staging with inability to auto-remediate.

| Time | Visual | Narration intent | Proof on screen |
| --- | --- | --- | --- |
| **0:00–0:20** | Title + one factory-camera still / architecture thumbnail | Problem: thermal throttling kills FPS before humans notice | Slide 1–2 |
| **0:20–0:45** | Architecture diagram | MongoDB = truth; Datadog = operator lens; Detect→Verify | Slide 3–4 |
| **0:45–1:20** | Simulator terminal heating + Datadog GPU widget | Live anomaly; investigate latency/FPS rising while network calm | Dashboard GPU + latency + FPS; Mongo incident OPEN |
| **1:20–1:55** | Start response-worker (or show already-open MITIGATING if auto) | Safe profile commanded; remediation action created | Logs `commanded_profile=safe`; Mongo remediation |
| **1:55–2:30** | Monitor ALERT → OK; device healthy | Continuous recovery evidence; RESOLVED | Monitor `333934695`; Mongo RESOLVED |
| **2:30–3:00** | Metrics table + closing | Synthetic but measured deltas; disclosure & future | Slide 7–8; evidence JSON optional flash |

## Shot list (priority)

1. Datadog dashboard `9rr-a4u-2st` — GPU crossing 85°C marker.  
2. Datadog monitor Alert state, then OK.  
3. MongoDB incident document (`detectedAt`, evidence, `resolvedAt`).  
4. Simulator line with `reported_profile=safe`.  
5. Log line containing `incident_id=` / `action_id=`.  

## What not to show

- `.env` or any key material.  
- Failed first-attempt HTTP 500 logs.  
- Claims of production camera counts.
