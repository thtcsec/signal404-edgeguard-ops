db = db.getSiblingDB("edgeguard");
const inc = db.incidents.findOne(
  { _id: "inc-thermal-edge-001-20261021113510" },
  { deviceId: 1, type: 1, status: 1, detectedAt: 1, resolvedAt: 1, remediationId: 1 }
);
const rem = db.remediation_actions.findOne(
  { _id: "act-safe-edge-001-20261021113514" },
  { deviceId: 1, actionType: 1, state: 1, requestedAt: 1, completedAt: 1 }
);
const dev = db.devices.findOne(
  { _id: "edge-001" },
  { name: 1, profile: 1, status: 1, site: 1, line: 1 }
);
const tel = db.telemetry.find({ "metadata.deviceId": "edge-001" }).sort({ timestamp: -1 }).limit(1).toArray()[0];
print("db.incidents.findOne({_id:'inc-thermal-edge-001-20261021113510'})");
printjson(inc);
print("db.remediation_actions.findOne({_id:'act-safe-edge-001-20261021113514'})");
printjson(rem);
print("db.devices.findOne({_id:'edge-001'})");
printjson(dev);
print("latest telemetry edge-001");
printjson({
  timestamp: tel && tel.timestamp,
  profile: tel && tel.profile,
  status: tel && tel.status,
  gpuTemperature: tel && tel.gpuTemperature,
  fps: tel && tel.fps,
  inferenceLatencyMs: tel && tel.inferenceLatencyMs
});
