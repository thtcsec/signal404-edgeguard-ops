using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using MongoDB.Driver;

namespace EdgeGuard.Shared.Persistence;

public sealed class MongoDeviceRepository : IDeviceRepository
{
    private readonly EdgeGuardMongoContext _context;

    public MongoDeviceRepository(EdgeGuardMongoContext context)
    {
        _context = context;
    }

    public async Task<DeviceRecord?> GetAsync(string deviceId, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var document = await _context.Devices
            .Find(x => x.Id == deviceId)
            .FirstOrDefaultAsync(cancellationToken);
        return document?.ToDomain();
    }

    public async Task UpsertAsync(DeviceRecord device, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var document = device.ToDocument();
        await _context.Devices.ReplaceOneAsync(
            x => x.Id == document.Id,
            document,
            new ReplaceOptions { IsUpsert = true },
            cancellationToken);
    }

    public async Task SetProfileAsync(string deviceId, DeviceProfile profile, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var update = Builders<DeviceDocument>.Update
            .Set(x => x.Profile, DomainMappings.FormatProfile(profile));

        var result = await _context.Devices.UpdateOneAsync(
            x => x.Id == deviceId,
            update,
            cancellationToken: cancellationToken);

        if (result.MatchedCount == 0)
        {
            throw new InvalidOperationException($"Device '{deviceId}' was not found when setting profile.");
        }
    }
}

public sealed class MongoTelemetryRepository : ITelemetryRepository
{
    private readonly EdgeGuardMongoContext _context;

    public MongoTelemetryRepository(EdgeGuardMongoContext context)
    {
        _context = context;
    }

    public async Task InsertAsync(TelemetryReading reading, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        await _context.Telemetry.InsertOneAsync(reading.ToDocument(), cancellationToken: cancellationToken);
    }

    public async Task<IReadOnlyList<TelemetryReading>> GetRecentAsync(
        string deviceId,
        TimeSpan lookback,
        CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var cutoff = DateTime.UtcNow.Subtract(lookback);
        var documents = await _context.Telemetry
            .Find(x => x.Metadata.DeviceId == deviceId && x.Timestamp >= cutoff)
            .SortByDescending(x => x.Timestamp)
            .ToListAsync(cancellationToken);
        return documents.Select(x => x.ToDomain()).ToList();
    }
}

public sealed class MongoIncidentRepository : IIncidentRepository
{
    private static readonly string[] ActiveStatuses =
    [
        DomainMappings.FormatIncidentStatus(IncidentStatus.Open),
        DomainMappings.FormatIncidentStatus(IncidentStatus.Investigating),
        DomainMappings.FormatIncidentStatus(IncidentStatus.Mitigating),
        DomainMappings.FormatIncidentStatus(IncidentStatus.Recovering)
    ];

    private readonly EdgeGuardMongoContext _context;

    public MongoIncidentRepository(EdgeGuardMongoContext context)
    {
        _context = context;
    }

    public async Task InsertAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        await _context.Incidents.InsertOneAsync(incident.ToDocument(), cancellationToken: cancellationToken);
    }

    public async Task<IncidentRecord?> GetAsync(string incidentId, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var document = await _context.Incidents
            .Find(x => x.Id == incidentId)
            .FirstOrDefaultAsync(cancellationToken);
        return document?.ToDomain();
    }

    public async Task<IncidentRecord?> FindActiveByDeviceAndTypeAsync(
        string deviceId,
        IncidentType type,
        CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var typeValue = DomainMappings.FormatIncidentType(type);

        var filter = Builders<IncidentDocument>.Filter.And(
            Builders<IncidentDocument>.Filter.Eq(x => x.DeviceId, deviceId),
            Builders<IncidentDocument>.Filter.Eq(x => x.Type, typeValue),
            Builders<IncidentDocument>.Filter.In(x => x.Status, ActiveStatuses));

        var document = await _context.Incidents
            .Find(filter)
            .SortByDescending(x => x.DetectedAt)
            .FirstOrDefaultAsync(cancellationToken);

        return document?.ToDomain();
    }

    public async Task<IReadOnlyList<IncidentRecord>> ListByStatusesAsync(
        IReadOnlyCollection<IncidentStatus> statuses,
        CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var statusValues = statuses.Select(DomainMappings.FormatIncidentStatus).ToArray();
        var documents = await _context.Incidents
            .Find(Builders<IncidentDocument>.Filter.In(x => x.Status, statusValues))
            .SortBy(x => x.DetectedAt)
            .ToListAsync(cancellationToken);
        return documents.Select(x => x.ToDomain()).ToList();
    }

    public async Task<int> CountActiveAsync(CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        return (int)await _context.Incidents.CountDocumentsAsync(
            Builders<IncidentDocument>.Filter.In(x => x.Status, ActiveStatuses),
            cancellationToken: cancellationToken);
    }

    public async Task UpdateAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        await _context.Incidents.ReplaceOneAsync(
            x => x.Id == incident.Id,
            incident.ToDocument(),
            cancellationToken: cancellationToken);
    }

    public async Task UpdateStatusAsync(
        string incidentId,
        IncidentStatus status,
        CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var update = Builders<IncidentDocument>.Update
            .Set(x => x.Status, DomainMappings.FormatIncidentStatus(status));

        if (status == IncidentStatus.Resolved)
        {
            update = update.Set(x => x.ResolvedAt, DateTime.UtcNow);
        }

        await _context.Incidents.UpdateOneAsync(
            x => x.Id == incidentId,
            update,
            cancellationToken: cancellationToken);
    }
}

public sealed class MongoRemediationActionRepository : IRemediationActionRepository
{
    private readonly EdgeGuardMongoContext _context;

    public MongoRemediationActionRepository(EdgeGuardMongoContext context)
    {
        _context = context;
    }

    public async Task InsertAsync(RemediationActionRecord action, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        await _context.RemediationActions.InsertOneAsync(
            action.ToDocument(),
            cancellationToken: cancellationToken);
    }

    public async Task<RemediationActionRecord?> GetAsync(string actionId, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        var document = await _context.RemediationActions
            .Find(x => x.Id == actionId)
            .FirstOrDefaultAsync(cancellationToken);
        return document?.ToDomain();
    }

    public async Task UpdateAsync(RemediationActionRecord action, CancellationToken cancellationToken)
    {
        await _context.EnsureInitializedAsync(cancellationToken);
        await _context.RemediationActions.ReplaceOneAsync(
            x => x.Id == action.Id,
            action.ToDocument(),
            cancellationToken: cancellationToken);
    }
}
