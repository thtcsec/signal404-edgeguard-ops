# Incident scenario

Planned demo only. The services in this repository do not detect, investigate, or remediate anything yet.

## Story

A factory line runs a small fleet of edge cameras. One camera, `edge-001` on `factory-a` / `line-03`, is the subject.

```text
Normal device
  -> temperature rises
  -> thermal throttling begins
  -> inference latency increases
  -> FPS decreases
  -> dropped frames increase
  -> monitoring detects degradation
  -> metrics, logs, and traces are correlated
  -> root cause is thermal throttling, not packet loss
  -> remediation switches the device to a safe workload profile
  -> temperature and latency recover
  -> the incident is verified and closed
```

## Operator timeline

| Phase | What the audience should see | Planned source |
| --- | --- | --- |
| Detect | GPU temperature and inference latency cross the monitor | Datadog monitor, fed by custom metrics |
| Investigate | 1-minute averages diverge from the 5-minute baseline; packet loss stays low | MongoDB `$setWindowFields`, logs, APM trace |
| Respond | Device profile changes from `full` to `safe` | Response worker and `remediation_actions` |
| Verify | Latency and temperature return, monitor OK, incident `RESOLVED` | New telemetry plus Datadog monitor state |

## Signals that identify the cause

Thermal throttling: rising CPU/GPU temperature, rising inference latency, falling FPS, rising dropped frames, stable packet loss and network latency.

Network degradation is a different future scenario: packet loss and network latency rise while temperature stays flat. The thermal demo has to show that distinction so the root cause is earned, not assumed.

## Remediation

The first action is `SWITCH_TO_SAFE_PROFILE`. `REDUCE_INFERENCE_RATE` and `RESTART_INFERENCE_SERVICE` exist as later options and are not selected for the primary demo unless the safe profile is not enough to show recovery in rehearsal.

## What is out of the story

No new computer-vision model, no training, and no live camera hardware. The fleet is synthetic. Production or employer data is not used. See [SECURITY.md](SECURITY.md).
