namespace EdgeGuard.Shared.Configuration;

public sealed class RemediationSettings
{
    public const string SectionName = "Remediation";

    public int PollIntervalSeconds { get; set; } = 5;

    /// <summary>
    /// Minimum time in RECOVERING before an incident may be marked RESOLVED.
    /// </summary>
    public int ObservationSeconds { get; set; } = 20;

    public double RecoveredGpuTemperatureMaxC { get; set; } = 75.0;

    public double RecoveredInferenceLatencyMaxMs { get; set; } = 80.0;

    public double RecoveredFpsMin { get; set; } = 18.0;

    public int RecentTelemetrySeconds { get; set; } = 30;
}
