using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Contracts;

public interface IDeviceRepository
{
    Task<DeviceRecord?> GetAsync(string deviceId, CancellationToken cancellationToken);

    Task UpsertAsync(DeviceRecord device, CancellationToken cancellationToken);
}

public interface ITelemetryRepository
{
    Task InsertAsync(TelemetryReading reading, CancellationToken cancellationToken);
}

public interface IIncidentRepository
{
    Task InsertAsync(IncidentRecord incident, CancellationToken cancellationToken);

    Task<IncidentRecord?> GetAsync(string incidentId, CancellationToken cancellationToken);

    Task<IncidentRecord?> FindActiveByDeviceAndTypeAsync(
        string deviceId,
        IncidentType type,
        CancellationToken cancellationToken);

    Task UpdateStatusAsync(
        string incidentId,
        IncidentStatus status,
        CancellationToken cancellationToken);
}

public interface IFleetHealthAnalyzer
{
    Task AnalyzeAsync(CancellationToken cancellationToken);
}

public interface IRemediationExecutor
{
    Task<RemediationActionRecord> ExecuteAsync(
        IncidentRecord incident,
        CancellationToken cancellationToken);
}
