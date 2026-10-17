using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Placeholders;

// Pre-hackathon placeholders kept for disclosure. Prefer Mongo* implementations in build-window code.

public sealed class UnimplementedDeviceRepository : IDeviceRepository
{
    public Task<DeviceRecord?> GetAsync(string deviceId, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<DeviceRecord?>();

    public Task UpsertAsync(DeviceRecord device, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();

    public Task SetProfileAsync(string deviceId, DeviceProfile profile, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

public sealed class UnimplementedTelemetryRepository : ITelemetryRepository
{
    public Task InsertAsync(TelemetryReading reading, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();

    public Task<IReadOnlyList<TelemetryReading>> GetRecentAsync(
        string deviceId,
        TimeSpan lookback,
        CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<IReadOnlyList<TelemetryReading>>();
}

public sealed class UnimplementedIncidentRepository : IIncidentRepository
{
    public Task InsertAsync(IncidentRecord incident, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();

    public Task<IncidentRecord?> GetAsync(string incidentId, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<IncidentRecord?>();

    public Task<IncidentRecord?> FindActiveByDeviceAndTypeAsync(
        string deviceId,
        IncidentType type,
        CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<IncidentRecord?>();

    public Task<IReadOnlyList<IncidentRecord>> ListByStatusesAsync(
        IReadOnlyCollection<IncidentStatus> statuses,
        CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<IReadOnlyList<IncidentRecord>>();

    public Task<int> CountActiveAsync(CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<int>();

    public Task UpdateAsync(IncidentRecord incident, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();

    public Task UpdateStatusAsync(
        string incidentId,
        IncidentStatus status,
        CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

public sealed class UnimplementedFleetHealthAnalyzer : IFleetHealthAnalyzer
{
    public Task AnalyzeAsync(CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

public sealed class UnimplementedRemediationExecutor : IRemediationExecutor
{
    public Task ProcessAsync(CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

public sealed class UnimplementedRemediationActionRepository : IRemediationActionRepository
{
    public Task InsertAsync(RemediationActionRecord action, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();

    public Task<RemediationActionRecord?> GetAsync(string actionId, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<RemediationActionRecord?>();

    public Task UpdateAsync(RemediationActionRecord action, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

internal static class PlaceholderResults
{
    public static Task NotReady() =>
        throw new NotSupportedException(
            "This operation is a pre-hackathon placeholder. Implement it during the official build window.");

    public static Task<T> NotReady<T>() =>
        throw new NotSupportedException(
            "This operation is a pre-hackathon placeholder. Implement it during the official build window.");
}
