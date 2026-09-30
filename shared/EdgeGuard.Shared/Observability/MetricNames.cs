namespace EdgeGuard.Shared.Observability;

public static class MetricNames
{
    public const string CpuUsage = "edgeguard.device.cpu_usage";
    public const string MemoryUsage = "edgeguard.device.memory_usage";
    public const string CpuTemperature = "edgeguard.device.cpu_temperature";
    public const string GpuTemperature = "edgeguard.device.gpu_temperature";
    public const string GpuUsage = "edgeguard.device.gpu_usage";
    public const string Fps = "edgeguard.device.fps";
    public const string InferenceLatency = "edgeguard.device.inference_latency";
    public const string PacketLoss = "edgeguard.device.packet_loss";
    public const string NetworkLatency = "edgeguard.device.network_latency";
    public const string DroppedFrames = "edgeguard.device.dropped_frames";
    public const string IncidentActive = "edgeguard.incident.active";
    public const string RemediationCount = "edgeguard.remediation.count";
}

public static class MetricTags
{
    public const string DeviceId = "device_id";
    public const string Site = "site";
    public const string Line = "line";
    public const string DeviceType = "device_type";
    public const string Profile = "profile";
    public const string IncidentType = "incident_type";
    public const string Severity = "severity";
}
