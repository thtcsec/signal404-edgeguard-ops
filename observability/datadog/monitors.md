# Monitor plans

Not created in Datadog. Suggested primary alert for the demo:

- Name: GPU temperature high on an edge device
- Query (draft): average of `edgeguard.device.gpu_temperature` grouped by `device_id`
- Meaning: thermal risk before the operator opens a camera view

Supporting alerts, same tags (`device_id`, `site`, `line`, `profile`):

- Inference latency above the device's recent baseline
- FPS below the line's operating threshold
- Packet loss above a small threshold (should not fire in the thermal demo)

Threshold numbers are decided when the simulator's synthetic ranges exist. They are not fixed here, so this file cannot be mistaken for a working monitor.
