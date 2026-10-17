# Data model

Planned MongoDB design for EdgeGuard Ops. None of these collections are created by the scaffold, and none of the queries below are executed.

Database name: `edgeguard`.

## devices

Regular collection. One document per fleet member. The simulator and remediation flow update `profile` and `status`.

```json
{
  "_id": "edge-001",
  "name": "Factory Camera 01",
  "site": "factory-a",
  "line": "line-03",
  "deviceType": "edge-camera",
  "hardware": {
    "cpu": "placeholder",
    "gpu": "placeholder"
  },
  "profile": "full",
  "status": "healthy",
  "createdAt": "2026-10-10T00:00:00Z"
}
```

Stored profile values: `full`, `reduced`, `safe`. Status values: `healthy`, `degraded`, `offline`.

Access pattern: point reads and updates by `_id`. Occasional listings by `site` and `line`. A compound index `{ site: 1, line: 1 }` is planned when the API starts listing devices.

## telemetry

Time-series collection. This is the primary operational dataset.

```text
timeField: timestamp
metaField: metadata
granularity: seconds
expireAfterSeconds: MongoDb:TelemetryExpireAfterSeconds (default 1209600, 14 days)
```

```json
{
  "timestamp": "2026-10-10T12:00:01Z",
  "metadata": {
    "deviceId": "edge-001",
    "site": "factory-a",
    "line": "line-03"
  },
  "cpuUsage": 55.2,
  "memoryUsage": 63.8,
  "cpuTemperature": 67.1,
  "gpuTemperature": 71.5,
  "gpuUsage": 82.0,
  "fps": 28.4,
  "inferenceLatencyMs": 41.3,
  "packetLossPct": 0.2,
  "networkLatencyMs": 12.5,
  "droppedFrames": 2,
  "profile": "full",
  "status": "healthy"
}
```

`deviceId` sits in `metadata` because filters and rollups are per device, site, and line, while the measurements change every sample. Keeping measurements at the top level makes the aggregation pipeline short and leaves metadata for grouping.

Access pattern: append-only inserts from the telemetry API. The analyzer reads a recent window for one device or one site. Time-series indexes cover that. Measurements are not updated in place.

Planned `createCollection` (not run by this scaffold):

```javascript
db.createCollection("telemetry", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "seconds"
  },
  expireAfterSeconds: 1209600
})
```

## incidents

Regular collection. One document per detected problem.

Lifecycle stored as strings:

```text
OPEN -> INVESTIGATING -> MITIGATING -> RECOVERING -> RESOLVED
```

```json
{
  "_id": "inc-001",
  "deviceId": "edge-001",
  "type": "thermal_throttling",
  "severity": "high",
  "status": "OPEN",
  "detectedAt": "2026-10-10T12:05:00Z",
  "resolvedAt": null,
  "evidence": {
    "gpuTemperature": 91.0,
    "inferenceLatencyMs": 180.0,
    "fps": 8.0,
    "droppedFrames": 40
  },
  "rootCause": null,
  "remediationId": null
}
```

Incident types reserved for the demo and alternate scenarios: `thermal_throttling`, `network_degradation`, `memory_pressure`.

Access pattern: insert on detect, update status and root cause during investigation and response, read open incidents for the response worker and the dashboard. Planned index: `{ status: 1, detectedAt: -1 }` and `{ deviceId: 1, detectedAt: -1 }`.

## remediation_actions

Regular collection, separate from incidents so a retry is visible without rewriting history.

```json
{
  "_id": "act-001",
  "incidentId": "inc-001",
  "deviceId": "edge-001",
  "actionType": "SWITCH_TO_SAFE_PROFILE",
  "state": "REQUESTED",
  "requestedAt": "2026-10-10T12:06:00Z",
  "completedAt": null
}
```

Action types: `SWITCH_TO_SAFE_PROFILE`, `REDUCE_INFERENCE_RATE`, `RESTART_INFERENCE_SERVICE`.

States: `REQUESTED`, `APPLIED`, `VERIFIED`, `FAILED`.

## Analytics

Implemented in `FleetThermalHealthAnalyzer` during the official build window.

### Rolling GPU temperature and inference latency

Compare the current 1-minute average with the previous 5-minute rolling average per device. `$setWindowFields` produces the 5-minute window; a `$group` or a second window covers the latest minute. A widening gap, with rising temperature and rising latency, is the thermal degradation signal.

```javascript
db.telemetry.aggregate([
  { $match: { timestamp: { $gte: ISODate("WINDOW_START") } } },
  { $setWindowFields: {
      partitionBy: "$metadata.deviceId",
      sortBy: { timestamp: 1 },
      output: {
        gpuTemp5m: {
          $avg: "$gpuTemperature",
          window: { range: [-5, 0], unit: "minute" }
        },
        latency5m: {
          $avg: "$inferenceLatencyMs",
          window: { range: [-5, 0], unit: "minute" }
        }
      }
  }}
])
```

The same window shape applies to FPS and dropped frames. Health rollups per device and per site use `$group` on `metadata.deviceId` or `metadata.site` over the chosen interval: average temperature, average latency, average FPS, sum of dropped frames, and last status.

### What "degradation" means in the demo

```text
current 1-minute average vs previous 5-minute rolling average
```

Temperature and inference latency moving up together, while packet loss stays low, distinguishes thermal throttling from network degradation. When the signal fires and no active incident exists for the device, an `OPEN` incident is inserted into `incidents`.
