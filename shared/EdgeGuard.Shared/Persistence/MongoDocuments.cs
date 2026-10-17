using EdgeGuard.Shared.Domain;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace EdgeGuard.Shared.Persistence;

public sealed class DeviceDocument
{
    [BsonId]
    public string Id { get; set; } = string.Empty;

    [BsonElement("name")]
    public string Name { get; set; } = string.Empty;

    [BsonElement("site")]
    public string Site { get; set; } = string.Empty;

    [BsonElement("line")]
    public string Line { get; set; } = string.Empty;

    [BsonElement("deviceType")]
    public string DeviceType { get; set; } = "edge-camera";

    [BsonElement("hardware")]
    public HardwareInfoDocument Hardware { get; set; } = new();

    [BsonElement("profile")]
    public string Profile { get; set; } = "full";

    [BsonElement("status")]
    public string Status { get; set; } = "healthy";

    [BsonElement("createdAt")]
    public DateTime CreatedAt { get; set; }
}

public sealed class HardwareInfoDocument
{
    [BsonElement("cpu")]
    public string Cpu { get; set; } = string.Empty;

    [BsonElement("gpu")]
    public string Gpu { get; set; } = string.Empty;
}

public sealed class TelemetryDocument
{
    [BsonId]
    [BsonIgnoreIfDefault]
    public ObjectId Id { get; set; }

    [BsonElement("timestamp")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime Timestamp { get; set; }

    [BsonElement("metadata")]
    public TelemetryMetadataDocument Metadata { get; set; } = new();

    [BsonElement("cpuUsage")]
    public double CpuUsage { get; set; }

    [BsonElement("memoryUsage")]
    public double MemoryUsage { get; set; }

    [BsonElement("cpuTemperature")]
    public double CpuTemperature { get; set; }

    [BsonElement("gpuTemperature")]
    public double GpuTemperature { get; set; }

    [BsonElement("gpuUsage")]
    public double GpuUsage { get; set; }

    [BsonElement("fps")]
    public double Fps { get; set; }

    [BsonElement("inferenceLatencyMs")]
    public double InferenceLatencyMs { get; set; }

    [BsonElement("packetLossPct")]
    public double PacketLossPct { get; set; }

    [BsonElement("networkLatencyMs")]
    public double NetworkLatencyMs { get; set; }

    [BsonElement("droppedFrames")]
    public int DroppedFrames { get; set; }

    [BsonElement("profile")]
    public string Profile { get; set; } = "full";

    [BsonElement("status")]
    public string Status { get; set; } = "healthy";
}

public sealed class TelemetryMetadataDocument
{
    [BsonElement("deviceId")]
    public string DeviceId { get; set; } = string.Empty;

    [BsonElement("site")]
    public string Site { get; set; } = string.Empty;

    [BsonElement("line")]
    public string Line { get; set; } = string.Empty;
}

public sealed class IncidentDocument
{
    [BsonId]
    public string Id { get; set; } = string.Empty;

    [BsonElement("deviceId")]
    public string DeviceId { get; set; } = string.Empty;

    [BsonElement("type")]
    public string Type { get; set; } = string.Empty;

    [BsonElement("severity")]
    public string Severity { get; set; } = string.Empty;

    [BsonElement("status")]
    public string Status { get; set; } = "OPEN";

    [BsonElement("detectedAt")]
    public DateTime DetectedAt { get; set; }

    [BsonElement("resolvedAt")]
    public DateTime? ResolvedAt { get; set; }

    [BsonElement("evidence")]
    public IncidentEvidenceDocument Evidence { get; set; } = new();

    [BsonElement("rootCause")]
    public string? RootCause { get; set; }

    [BsonElement("remediationId")]
    public string? RemediationId { get; set; }
}

public sealed class IncidentEvidenceDocument
{
    [BsonElement("gpuTemperature")]
    public double? GpuTemperature { get; set; }

    [BsonElement("inferenceLatencyMs")]
    public double? InferenceLatencyMs { get; set; }

    [BsonElement("fps")]
    public double? Fps { get; set; }

    [BsonElement("droppedFrames")]
    public int? DroppedFrames { get; set; }
}

public sealed class RemediationActionDocument
{
    [BsonId]
    public string Id { get; set; } = string.Empty;

    [BsonElement("incidentId")]
    public string IncidentId { get; set; } = string.Empty;

    [BsonElement("deviceId")]
    public string DeviceId { get; set; } = string.Empty;

    [BsonElement("actionType")]
    public string ActionType { get; set; } = string.Empty;

    [BsonElement("state")]
    public string State { get; set; } = "REQUESTED";

    [BsonElement("requestedAt")]
    public DateTime RequestedAt { get; set; }

    [BsonElement("completedAt")]
    public DateTime? CompletedAt { get; set; }
}
