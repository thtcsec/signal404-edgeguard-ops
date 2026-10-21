db = db.getSiblingDB("edgeguard");
const inc = db.incidents.find().sort({ detectedAt: -1 }).limit(1).toArray()[0] || null;
const rem = inc && inc.remediationId
  ? db.remediation_actions.findOne({ _id: inc.remediationId })
  : db.remediation_actions.find().sort({ requestedAt: -1 }).limit(1).toArray()[0];
const dev = db.devices.findOne({ _id: "edge-001" }, { name: 1, profile: 1, status: 1, site: 1, line: 1 });
const tel = db.telemetry.find({ "metadata.deviceId": "edge-001" }).sort({ timestamp: -1 }).limit(1).toArray()[0] || null;
print("db.incidents.find().sort({detectedAt:-1}).limit(1)");
printjson(inc && {
  _id: inc._id,
  deviceId: inc.deviceId,
  type: inc.type,
  status: inc.status,
  detectedAt: inc.detectedAt,
  resolvedAt: inc.resolvedAt,
  remediationId: inc.remediationId
});
print("db.remediation_actions.findOne({_id: remediationId})");
printjson(rem && {
  _id: rem._id,
  incidentId: rem.incidentId,
  deviceId: rem.deviceId,
  actionType: rem.actionType,
  state: rem.state,
  requestedAt: rem.requestedAt,
  completedAt: rem.completedAt
});
print("db.devices.findOne({_id:'edge-001'})");
printjson(dev);
print("db.telemetry.find({deviceId:'edge-001'}).sort({timestamp:-1}).limit(1)");
printjson(tel && {
  timestamp: tel.timestamp,
  profile: tel.profile,
  status: tel.status,
  gpuTemperature: tel.gpuTemperature,
  fps: tel.fps,
  inferenceLatencyMs: tel.inferenceLatencyMs
});
