namespace EdgeGuard.Shared.Contracts;

public sealed record TelemetryIngestRequest(
    string DeviceId,
    string Site,
    string Line,
    DateTimeOffset Timestamp,
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
    string Profile,
    string Status);
