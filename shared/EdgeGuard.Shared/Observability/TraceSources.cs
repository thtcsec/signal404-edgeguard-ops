using System.Diagnostics;

namespace EdgeGuard.Shared.Observability;

public static class TraceSources
{
    public const string Name = "EdgeGuard.Ops";

    public static readonly ActivitySource ActivitySource = new(Name);

    public const string IngestTelemetry = "POST /telemetry";
    public const string InsertTelemetry = "TelemetryRepository.insert";
    public const string AnalyzeFleet = "HealthAnalyzer.analyze";
    public const string OpenIncident = "IncidentRepository.insert";
    public const string ExecuteRemediation = "RemediationExecutor.execute";
}
