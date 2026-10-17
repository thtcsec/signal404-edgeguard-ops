namespace EdgeGuard.Shared.Configuration;

public sealed class RemediationSettings
{
    public const string SectionName = "Remediation";

    public int PollIntervalSeconds { get; set; } = 5;

    /// <summary>
    /// Minimum continuous healthy observation window before RESOLVED.
    /// </summary>
    public int ObservationSeconds { get; set; } = 20;

    public double RecoveredGpuTemperatureMaxC { get; set; } = 75.0;

    public double RecoveredInferenceLatencyMaxMs { get; set; } = 80.0;

    public double RecoveredFpsMin { get; set; } = 18.0;

    public int RecentTelemetrySeconds { get; set; } = 45;

    /// <summary>
    /// Latest sample must be newer than this or recovery evidence is considered stale
    /// (e.g. simulator stopped mid-recovery).
    /// </summary>
    public int MaxTelemetryStalenessSeconds { get; set; } = 5;

    /// <summary>
    /// Maximum gap between consecutive healthy samples inside the observation window.
    /// Larger gaps reset the observation clock.
    /// </summary>
    public int MaxSampleGapSeconds { get; set; } = 5;

    public int MinHealthySamples { get; set; } = 3;
}
