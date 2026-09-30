namespace EdgeGuard.Shared.Domain;

public sealed record IncidentEvidence(
    double? GpuTemperature,
    double? InferenceLatencyMs,
    double? Fps,
    int? DroppedFrames);

public sealed record IncidentRecord(
    string Id,
    string DeviceId,
    IncidentType Type,
    IncidentSeverity Severity,
    IncidentStatus Status,
    DateTimeOffset DetectedAt,
    DateTimeOffset? ResolvedAt,
    IncidentEvidence Evidence,
    string? RootCause,
    string? RemediationId);
