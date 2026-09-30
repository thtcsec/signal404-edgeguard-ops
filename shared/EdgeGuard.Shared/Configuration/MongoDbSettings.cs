namespace EdgeGuard.Shared.Configuration;

public sealed class MongoDbSettings
{
    public const string SectionName = "MongoDb";

    public string ConnectionString { get; set; } = "mongodb://localhost:27017";

    public string DatabaseName { get; set; } = "edgeguard";

    public string DevicesCollection { get; set; } = "devices";

    public string TelemetryCollection { get; set; } = "telemetry";

    public string IncidentsCollection { get; set; } = "incidents";

    public string RemediationActionsCollection { get; set; } = "remediation_actions";

    public string TelemetryTimeField { get; set; } = "timestamp";

    public string TelemetryMetaField { get; set; } = "metadata";

    public string TelemetryGranularity { get; set; } = "seconds";

    /// <summary>
    /// Planned TTL for telemetry time-series documents. Collection creation is a build-window task.
    /// </summary>
    public int TelemetryExpireAfterSeconds { get; set; } = 1_209_600;
}
