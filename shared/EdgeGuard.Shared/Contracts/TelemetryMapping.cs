using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Persistence;

namespace EdgeGuard.Shared.Contracts;

public static class TelemetryMapping
{
    public static TelemetryReading ToReading(this TelemetryIngestRequest request)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(request.DeviceId);
        ArgumentException.ThrowIfNullOrWhiteSpace(request.Site);
        ArgumentException.ThrowIfNullOrWhiteSpace(request.Line);

        return new TelemetryReading(
            request.Timestamp == default ? DateTimeOffset.UtcNow : request.Timestamp,
            new TelemetryMetadata(request.DeviceId, request.Site, request.Line),
            request.CpuUsage,
            request.MemoryUsage,
            request.CpuTemperature,
            request.GpuTemperature,
            request.GpuUsage,
            request.Fps,
            request.InferenceLatencyMs,
            request.PacketLossPct,
            request.NetworkLatencyMs,
            request.DroppedFrames,
            DomainMappings.ParseProfile(string.IsNullOrWhiteSpace(request.Profile) ? "full" : request.Profile),
            DomainMappings.ParseStatus(string.IsNullOrWhiteSpace(request.Status) ? "healthy" : request.Status));
    }
}
