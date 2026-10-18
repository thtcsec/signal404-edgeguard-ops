namespace EdgeGuard.Shared.Configuration;

public sealed class ObservabilitySettings
{
    public const string SectionName = "Observability";

    public string ServiceName { get; set; } = "edgeguard";

    /// <summary>
    /// When false, metrics use NoOp and the stack still runs without an agent.
    /// </summary>
    public bool DatadogEnabled { get; set; }

    public string AgentHost { get; set; } = "127.0.0.1";

    public int DogStatsDPort { get; set; } = 8125;

    public int TraceAgentPort { get; set; } = 8126;

    public string EnvironmentName { get; set; } = "development";

    public string Version { get; set; } = "0.1.0";

    /// <summary>
    /// When Datadog is enabled, JSON logs are also written under this directory for Agent file-tail.
    /// Default is repo-relative <c>.logs</c> (mounted into the Compose agent).
    /// </summary>
    public string LogDirectory { get; set; } = ".logs";
}
