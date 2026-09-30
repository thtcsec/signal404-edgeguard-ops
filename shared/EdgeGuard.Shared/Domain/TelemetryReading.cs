namespace EdgeGuard.Shared.Domain;

public sealed record TelemetryMetadata(string DeviceId, string Site, string Line);

public sealed record TelemetryReading(
    DateTimeOffset Timestamp,
    TelemetryMetadata Metadata,
    double CpuUsage,
    double MemoryUsage,
    double CpuTemperature,
    double GpuTemperature,
    double GpuUsage,
    double Fps,
    double InferenceLatencyMs,
    double PacketLossPct,
    double NetworkLatencyMs,
    int DroppedFrames,
    DeviceProfile Profile,
    DeviceStatus Status);
