db = db.getSiblingDB("edgeguard");
print("=== INCIDENT ===");
printjson(db.incidents.find().sort({ detectedAt: -1 }).limit(1).toArray()[0]);
print("=== REMEDIATION ===");
printjson(db.remediation_actions.find().sort({ requestedAt: -1 }).limit(1).toArray()[0]);
print("=== DEVICE (_id=edge-001) ===");
printjson(db.devices.findOne({ _id: "edge-001" }));
print("=== LAST 5 TELEMETRY ===");
printjson(db.telemetry.find({ "metadata.deviceId": "edge-001" }).sort({ timestamp: -1 }).limit(5).toArray());
