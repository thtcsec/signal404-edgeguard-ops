using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Persistence;

public static class DomainMappings
{
    public static DeviceDocument ToDocument(this DeviceRecord device) =>
        new()
        {
            Id = device.Id,
            Name = device.Name,
            Site = device.Site,
            Line = device.Line,
            DeviceType = device.DeviceType,
            Hardware = new HardwareInfoDocument
            {
                Cpu = device.Hardware.Cpu,
                Gpu = device.Hardware.Gpu
            },
            Profile = FormatProfile(device.Profile),
            Status = FormatStatus(device.Status),
            CreatedAt = device.CreatedAt.UtcDateTime
        };

    public static DeviceRecord ToDomain(this DeviceDocument document) =>
        new(
            document.Id,
            document.Name,
            document.Site,
            document.Line,
            document.DeviceType,
            new HardwareInfo(document.Hardware.Cpu, document.Hardware.Gpu),
            ParseProfile(document.Profile),
            ParseStatus(document.Status),
            new DateTimeOffset(DateTime.SpecifyKind(document.CreatedAt, DateTimeKind.Utc)));

    public static TelemetryDocument ToDocument(this TelemetryReading reading) =>
        new()
        {
            Timestamp = DateTime.SpecifyKind(reading.Timestamp.UtcDateTime, DateTimeKind.Utc),
            Metadata = new TelemetryMetadataDocument
            {
                DeviceId = reading.Metadata.DeviceId,
                Site = reading.Metadata.Site,
                Line = reading.Metadata.Line
            },
            CpuUsage = reading.CpuUsage,
            MemoryUsage = reading.MemoryUsage,
            CpuTemperature = reading.CpuTemperature,
            GpuTemperature = reading.GpuTemperature,
            GpuUsage = reading.GpuUsage,
            Fps = reading.Fps,
            InferenceLatencyMs = reading.InferenceLatencyMs,
            PacketLossPct = reading.PacketLossPct,
            NetworkLatencyMs = reading.NetworkLatencyMs,
            DroppedFrames = reading.DroppedFrames,
            Profile = FormatProfile(reading.Profile),
            Status = FormatStatus(reading.Status)
        };

    public static TelemetryReading ToDomain(this TelemetryDocument document) =>
        new(
            new DateTimeOffset(DateTime.SpecifyKind(document.Timestamp, DateTimeKind.Utc)),
            new TelemetryMetadata(
                document.Metadata.DeviceId,
                document.Metadata.Site,
                document.Metadata.Line),
            document.CpuUsage,
            document.MemoryUsage,
            document.CpuTemperature,
            document.GpuTemperature,
            document.GpuUsage,
            document.Fps,
            document.InferenceLatencyMs,
            document.PacketLossPct,
            document.NetworkLatencyMs,
            document.DroppedFrames,
            ParseProfile(document.Profile),
            ParseStatus(document.Status));

    public static IncidentDocument ToDocument(this IncidentRecord incident) =>
        new()
        {
            Id = incident.Id,
            DeviceId = incident.DeviceId,
            Type = FormatIncidentType(incident.Type),
            Severity = incident.Severity.ToString().ToLowerInvariant(),
            Status = FormatIncidentStatus(incident.Status),
            DetectedAt = incident.DetectedAt.UtcDateTime,
            ResolvedAt = incident.ResolvedAt?.UtcDateTime,
            Evidence = new IncidentEvidenceDocument
            {
                GpuTemperature = incident.Evidence.GpuTemperature,
                InferenceLatencyMs = incident.Evidence.InferenceLatencyMs,
                Fps = incident.Evidence.Fps,
                DroppedFrames = incident.Evidence.DroppedFrames
            },
            RootCause = incident.RootCause,
            RemediationId = incident.RemediationId
        };

    public static IncidentRecord ToDomain(this IncidentDocument document) =>
        new(
            document.Id,
            document.DeviceId,
            ParseIncidentType(document.Type),
            Enum.Parse<IncidentSeverity>(document.Severity, ignoreCase: true),
            ParseIncidentStatus(document.Status),
            new DateTimeOffset(DateTime.SpecifyKind(document.DetectedAt, DateTimeKind.Utc)),
            document.ResolvedAt is null
                ? null
                : new DateTimeOffset(DateTime.SpecifyKind(document.ResolvedAt.Value, DateTimeKind.Utc)),
            new IncidentEvidence(
                document.Evidence.GpuTemperature,
                document.Evidence.InferenceLatencyMs,
                document.Evidence.Fps,
                document.Evidence.DroppedFrames),
            document.RootCause,
            document.RemediationId);

    public static string FormatProfile(DeviceProfile profile) =>
        profile switch
        {
            DeviceProfile.Full => "full",
            DeviceProfile.Reduced => "reduced",
            DeviceProfile.Safe => "safe",
            _ => profile.ToString().ToLowerInvariant()
        };

    public static DeviceProfile ParseProfile(string value) =>
        value.ToLowerInvariant() switch
        {
            "full" => DeviceProfile.Full,
            "reduced" => DeviceProfile.Reduced,
            "safe" => DeviceProfile.Safe,
            _ => Enum.Parse<DeviceProfile>(value, ignoreCase: true)
        };

    public static string FormatStatus(DeviceStatus status) =>
        status.ToString().ToLowerInvariant();

    public static DeviceStatus ParseStatus(string value) =>
        Enum.Parse<DeviceStatus>(value, ignoreCase: true);

    public static string FormatIncidentStatus(IncidentStatus status) =>
        status switch
        {
            IncidentStatus.Open => "OPEN",
            IncidentStatus.Investigating => "INVESTIGATING",
            IncidentStatus.Mitigating => "MITIGATING",
            IncidentStatus.Recovering => "RECOVERING",
            IncidentStatus.Resolved => "RESOLVED",
            _ => status.ToString().ToUpperInvariant()
        };

    public static IncidentStatus ParseIncidentStatus(string value) =>
        value.ToUpperInvariant() switch
        {
            "OPEN" => IncidentStatus.Open,
            "INVESTIGATING" => IncidentStatus.Investigating,
            "MITIGATING" => IncidentStatus.Mitigating,
            "RECOVERING" => IncidentStatus.Recovering,
            "RESOLVED" => IncidentStatus.Resolved,
            _ => Enum.Parse<IncidentStatus>(value, ignoreCase: true)
        };

    public static string FormatIncidentType(IncidentType type) =>
        type switch
        {
            IncidentType.ThermalThrottling => "thermal_throttling",
            IncidentType.NetworkDegradation => "network_degradation",
            IncidentType.MemoryPressure => "memory_pressure",
            _ => type.ToString().ToLowerInvariant()
        };

    public static IncidentType ParseIncidentType(string value) =>
        value.ToLowerInvariant() switch
        {
            "thermal_throttling" => IncidentType.ThermalThrottling,
            "network_degradation" => IncidentType.NetworkDegradation,
            "memory_pressure" => IncidentType.MemoryPressure,
            _ => Enum.Parse<IncidentType>(value, ignoreCase: true)
        };

    public static RemediationActionDocument ToDocument(this RemediationActionRecord action) =>
        new()
        {
            Id = action.Id,
            IncidentId = action.IncidentId,
            DeviceId = action.DeviceId,
            ActionType = FormatRemediationAction(action.ActionType),
            State = FormatRemediationState(action.State),
            RequestedAt = action.RequestedAt.UtcDateTime,
            CompletedAt = action.CompletedAt?.UtcDateTime
        };

    public static RemediationActionRecord ToDomain(this RemediationActionDocument document) =>
        new(
            document.Id,
            document.IncidentId,
            document.DeviceId,
            ParseRemediationAction(document.ActionType),
            ParseRemediationState(document.State),
            new DateTimeOffset(DateTime.SpecifyKind(document.RequestedAt, DateTimeKind.Utc)),
            document.CompletedAt is null
                ? null
                : new DateTimeOffset(DateTime.SpecifyKind(document.CompletedAt.Value, DateTimeKind.Utc)));

    public static string FormatRemediationAction(RemediationActionType type) =>
        type switch
        {
            RemediationActionType.SwitchToSafeProfile => "SWITCH_TO_SAFE_PROFILE",
            RemediationActionType.ReduceInferenceRate => "REDUCE_INFERENCE_RATE",
            RemediationActionType.RestartInferenceService => "RESTART_INFERENCE_SERVICE",
            _ => type.ToString().ToUpperInvariant()
        };

    public static RemediationActionType ParseRemediationAction(string value) =>
        value.ToUpperInvariant() switch
        {
            "SWITCH_TO_SAFE_PROFILE" => RemediationActionType.SwitchToSafeProfile,
            "REDUCE_INFERENCE_RATE" => RemediationActionType.ReduceInferenceRate,
            "RESTART_INFERENCE_SERVICE" => RemediationActionType.RestartInferenceService,
            _ => Enum.Parse<RemediationActionType>(value, ignoreCase: true)
        };

    public static string FormatRemediationState(RemediationState state) =>
        state.ToString().ToUpperInvariant();

    public static RemediationState ParseRemediationState(string value) =>
        Enum.Parse<RemediationState>(value, ignoreCase: true);
}
