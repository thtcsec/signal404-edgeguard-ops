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
}

public sealed class MongoIncidentRepository : IIncidentRepository
{
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
