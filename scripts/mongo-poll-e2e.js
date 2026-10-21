db = db.getSiblingDB("edgeguard");
const inc = db.incidents.find().sort({ detectedAt: -1 }).limit(1).toArray()[0] || null;
const rem = db.remediation_actions.find().sort({ requestedAt: -1 }).limit(1).toArray()[0] || null;
const dev = db.devices.findOne({ _id: "edge-001" });
const tel = db.telemetry.find({ "metadata.deviceId": "edge-001" }).sort({ timestamp: -1 }).limit(1).toArray()[0] || null;
function iso(v) {
  if (v == null) return null;
  if (v instanceof Date) return v.toISOString();
  return v;
}
print(JSON.stringify({
  incident: inc && {
    _id: inc._id,
    deviceId: inc.deviceId,
    status: inc.status,
    type: inc.type,
    detectedAt: iso(inc.detectedAt),
    resolvedAt: iso(inc.resolvedAt),
    remediationId: inc.remediationId
  },
  remediation: rem && {
    _id: rem._id,
    incidentId: rem.incidentId,
    deviceId: rem.deviceId,
    state: rem.state,
    actionType: rem.actionType,
    requestedAt: iso(rem.requestedAt),
    completedAt: iso(rem.completedAt)
  },
  device: dev && {
    _id: dev._id,
    profile: dev.profile,
    status: dev.status,
    name: dev.name
  },
  telemetry: tel && {
    timestamp: iso(tel.timestamp),
    profile: tel.profile,
    status: tel.status,
    gpuTemperature: tel.gpuTemperature,
    fps: tel.fps,
    inferenceLatencyMs: tel.inferenceLatencyMs,
    deviceId: tel.metadata && tel.metadata.deviceId
  }
}));
