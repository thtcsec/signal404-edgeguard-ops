using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Contracts;

public interface IDeviceRepository
{
    Task<DeviceRecord?> GetAsync(string deviceId, CancellationToken cancellationToken);

    Task UpsertAsync(DeviceRecord device, CancellationToken cancellationToken);

    Task SetProfileAsync(string deviceId, DeviceProfile profile, CancellationToken cancellationToken);
}

public interface ITelemetryRepository
{
    Task InsertAsync(TelemetryReading reading, CancellationToken cancellationToken);

    Task<IReadOnlyList<TelemetryReading>> GetRecentAsync(
        string deviceId,
        TimeSpan lookback,
        CancellationToken cancellationToken);
}

public interface IIncidentRepository
{
    Task InsertAsync(IncidentRecord incident, CancellationToken cancellationToken);

    Task<IncidentRecord?> GetAsync(string incidentId, CancellationToken cancellationToken);

    Task<IncidentRecord?> FindActiveByDeviceAndTypeAsync(
        string deviceId,
        IncidentType type,
        CancellationToken cancellationToken);

    Task<IReadOnlyList<IncidentRecord>> ListByStatusesAsync(
        IReadOnlyCollection<IncidentStatus> statuses,
        CancellationToken cancellationToken);

    Task<int> CountActiveAsync(CancellationToken cancellationToken);

    Task UpdateAsync(IncidentRecord incident, CancellationToken cancellationToken);

    Task UpdateStatusAsync(
        string incidentId,
        IncidentStatus status,
        CancellationToken cancellationToken);
}

public interface IRemediationActionRepository
{
    Task InsertAsync(RemediationActionRecord action, CancellationToken cancellationToken);

    Task<RemediationActionRecord?> GetAsync(string actionId, CancellationToken cancellationToken);

    Task UpdateAsync(RemediationActionRecord action, CancellationToken cancellationToken);
}

public interface IFleetHealthAnalyzer
{
    Task AnalyzeAsync(CancellationToken cancellationToken);
}

public interface IRemediationExecutor
{
    Task ProcessAsync(CancellationToken cancellationToken);
}
