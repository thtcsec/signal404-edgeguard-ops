using EdgeGuard.Shared.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using MongoDB.Bson;
using MongoDB.Driver;

namespace EdgeGuard.Shared.Persistence;

public sealed class EdgeGuardMongoContext
{
    private readonly IMongoDatabase _database;
    private readonly MongoDbSettings _settings;
    private readonly ILogger<EdgeGuardMongoContext> _logger;
    private readonly SemaphoreSlim _initializeLock = new(1, 1);
    private bool _initialized;

    public EdgeGuardMongoContext(
        IOptions<MongoDbSettings> options,
        ILogger<EdgeGuardMongoContext> logger)
    {
        _settings = options.Value;
        _logger = logger;

        var client = new MongoClient(_settings.ConnectionString);
        _database = client.GetDatabase(_settings.DatabaseName);
    }

    public IMongoCollection<DeviceDocument> Devices =>
        _database.GetCollection<DeviceDocument>(_settings.DevicesCollection);

    public IMongoCollection<TelemetryDocument> Telemetry =>
        _database.GetCollection<TelemetryDocument>(_settings.TelemetryCollection);

    public IMongoCollection<IncidentDocument> Incidents =>
        _database.GetCollection<IncidentDocument>(_settings.IncidentsCollection);

    public IMongoCollection<RemediationActionDocument> RemediationActions =>
        _database.GetCollection<RemediationActionDocument>(_settings.RemediationActionsCollection);

    public async Task EnsureInitializedAsync(CancellationToken cancellationToken)
    {
        if (_initialized)
        {
            return;
        }

        await _initializeLock.WaitAsync(cancellationToken);
        try
        {
            if (_initialized)
            {
                return;
            }

            await EnsureTelemetryTimeSeriesAsync(cancellationToken);
            await EnsureRegularCollectionAsync(_settings.DevicesCollection, cancellationToken);
            await EnsureRegularCollectionAsync(_settings.IncidentsCollection, cancellationToken);
            await EnsureRegularCollectionAsync(_settings.RemediationActionsCollection, cancellationToken);
            await EnsureIndexesAsync(cancellationToken);

            _initialized = true;
            _logger.LogInformation(
                "MongoDB initialized for database {Database}. Telemetry TTL={ExpireAfterSeconds}s.",
                _settings.DatabaseName,
                _settings.TelemetryExpireAfterSeconds);
        }
        finally
        {
            _initializeLock.Release();
        }
    }

    private async Task EnsureTelemetryTimeSeriesAsync(CancellationToken cancellationToken)
    {
        var names = await (await _database.ListCollectionNamesAsync(cancellationToken: cancellationToken))
            .ToListAsync(cancellationToken);

        if (names.Contains(_settings.TelemetryCollection, StringComparer.Ordinal))
        {
            return;
        }

        var options = new CreateCollectionOptions
        {
            ExpireAfter = TimeSpan.FromSeconds(_settings.TelemetryExpireAfterSeconds),
            TimeSeriesOptions = new TimeSeriesOptions(
                _settings.TelemetryTimeField,
                _settings.TelemetryMetaField,
                TimeSeriesGranularity.Seconds)
        };

        await _database.CreateCollectionAsync(
            _settings.TelemetryCollection,
            options,
            cancellationToken);

        _logger.LogInformation(
            "Created time-series collection {Collection} (timeField={TimeField}, metaField={MetaField}).",
            _settings.TelemetryCollection,
            _settings.TelemetryTimeField,
            _settings.TelemetryMetaField);
    }

    private async Task EnsureRegularCollectionAsync(string collectionName, CancellationToken cancellationToken)
    {
        var names = await (await _database.ListCollectionNamesAsync(cancellationToken: cancellationToken))
            .ToListAsync(cancellationToken);

        if (names.Contains(collectionName, StringComparer.Ordinal))
        {
            return;
        }

        await _database.CreateCollectionAsync(collectionName, cancellationToken: cancellationToken);
        _logger.LogInformation("Created collection {Collection}.", collectionName);
    }

    private async Task EnsureIndexesAsync(CancellationToken cancellationToken)
    {
        await Devices.Indexes.CreateOneAsync(
            new CreateIndexModel<DeviceDocument>(
                Builders<DeviceDocument>.IndexKeys
                    .Ascending(x => x.Site)
                    .Ascending(x => x.Line)),
            cancellationToken: cancellationToken);

        await Incidents.Indexes.CreateOneAsync(
            new CreateIndexModel<IncidentDocument>(
                Builders<IncidentDocument>.IndexKeys
                    .Ascending(x => x.Status)
                    .Descending(x => x.DetectedAt)),
            cancellationToken: cancellationToken);

        await Incidents.Indexes.CreateOneAsync(
            new CreateIndexModel<IncidentDocument>(
                Builders<IncidentDocument>.IndexKeys
                    .Ascending(x => x.DeviceId)
                    .Descending(x => x.DetectedAt)),
            cancellationToken: cancellationToken);
    }

    public async Task<bool> CanPingAsync(CancellationToken cancellationToken)
    {
        try
        {
            await _database.RunCommandAsync<BsonDocument>(
                new BsonDocument("ping", 1),
                cancellationToken: cancellationToken);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "MongoDB ping failed.");
            return false;
        }
    }
}
