using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Observability;

public interface IOperationalTelemetry
{
    void RecordDeviceSample(TelemetryReading reading);

    void RecordActiveIncidents(int count);

    void RecordRemediation(RemediationActionType actionType);
}

/// <summary>
/// Does not emit metrics. Replace with a DogStatsD implementation during the build window.
/// </summary>
public sealed class NoOpOperationalTelemetry : IOperationalTelemetry
{
    public void RecordDeviceSample(TelemetryReading reading)
    {
    }

    public void RecordActiveIncidents(int count)
    {
    }

    public void RecordRemediation(RemediationActionType actionType)
    {
    }
}
