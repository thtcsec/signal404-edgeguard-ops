namespace EdgeGuard.Shared.Configuration;

public sealed class ObservabilitySettings
{
    public const string SectionName = "Observability";

    public string ServiceName { get; set; } = "edgeguard";

    /// <summary>
    /// Stays false until Datadog tracing and DogStatsD are wired during the build window.
    /// </summary>
    public bool DatadogEnabled { get; set; }

    public string AgentHost { get; set; } = "127.0.0.1";

    public int DogStatsDPort { get; set; } = 8125;

    public int TraceAgentPort { get; set; } = 8126;
}
