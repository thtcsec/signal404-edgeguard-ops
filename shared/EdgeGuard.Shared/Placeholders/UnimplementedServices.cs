using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Shared.Placeholders;

// Pre-hackathon placeholders. Replace these types during 2026-10-10 to 2026-10-24.

public sealed class UnimplementedDeviceRepository : IDeviceRepository
{
    public Task<DeviceRecord?> GetAsync(string deviceId, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<DeviceRecord?>();

    public Task UpsertAsync(DeviceRecord device, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
}

public sealed class UnimplementedTelemetryRepository : ITelemetryRepository
{
    public Task InsertAsync(TelemetryReading reading, CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady();
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
    public Task<RemediationActionRecord> ExecuteAsync(
        IncidentRecord incident,
        CancellationToken cancellationToken) =>
        PlaceholderResults.NotReady<RemediationActionRecord>();
}

internal static class PlaceholderResults
{
    public static Task NotReady() =>
        throw new NotSupportedException(
            "This operation is a pre-hackathon placeholder. Implement it during 2026-10-10 to 2026-10-24.");

    public static Task<T> NotReady<T>() =>
        throw new NotSupportedException(
            "This operation is a pre-hackathon placeholder. Implement it during 2026-10-10 to 2026-10-24.");
}
