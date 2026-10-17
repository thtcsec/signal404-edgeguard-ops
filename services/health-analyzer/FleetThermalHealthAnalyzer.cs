using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;
using EdgeGuard.Shared.Persistence;
using Microsoft.Extensions.Options;
using MongoDB.Bson;
using MongoDB.Driver;

namespace EdgeGuard.HealthAnalyzer;

public sealed class FleetThermalHealthAnalyzer : IFleetHealthAnalyzer
{
    private readonly EdgeGuardMongoContext _mongo;
    private readonly IIncidentRepository _incidents;
    private readonly IOperationalTelemetry _telemetry;
    private readonly AnalyzerSettings _settings;
    private readonly ILogger<FleetThermalHealthAnalyzer> _logger;

    public FleetThermalHealthAnalyzer(
        EdgeGuardMongoContext mongo,
        IIncidentRepository incidents,
        IOperationalTelemetry telemetry,
        IOptions<AnalyzerSettings> settings,
        ILogger<FleetThermalHealthAnalyzer> logger)
    {
        _mongo = mongo;
        _incidents = incidents;
        _telemetry = telemetry;
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task AnalyzeAsync(CancellationToken cancellationToken)
    {
        using var activity = TraceSources.ActivitySource.StartActivity(TraceSources.AnalyzeFleet);

        await _mongo.EnsureInitializedAsync(cancellationToken);
        var snapshots = await EvaluateDeviceTrendsAsync(cancellationToken);
        var opened = 0;

        foreach (var snapshot in snapshots)
        {
            if (!IsThermalIncident(snapshot))
            {
                continue;
            }

            var existing = await _incidents.FindActiveByDeviceAndTypeAsync(
                snapshot.DeviceId,
                IncidentType.ThermalThrottling,
                cancellationToken);

            if (existing is not null)
            {
                _logger.LogDebug(
                    "Active thermal incident already open for {DeviceId}: {IncidentId}",
                    snapshot.DeviceId,
                    existing.Id);
                continue;
            }

            var incident = CreateIncident(snapshot);
            using (TraceSources.ActivitySource.StartActivity(TraceSources.OpenIncident))
            {
                await _incidents.InsertAsync(incident, cancellationToken);
            }

            opened++;
            _logger.LogWarning(
                "Opened thermal incident {IncidentId} for {DeviceId}: gpu1m={Gpu1m:F1}C gpu5m={Gpu5m:F1}C latency1m={Latency1m:F1}ms fps1m={Fps1m:F1} packetLoss1m={PacketLoss:F2}% netLatency1m={NetLatency:F1}ms",
                incident.Id,
                snapshot.DeviceId,
                snapshot.GpuTemp1m,
                snapshot.GpuTemp5m,
                snapshot.Latency1m,
                snapshot.Fps1m,
                snapshot.PacketLoss1m,
                snapshot.NetworkLatency1m);
        }

        var activeCount = await _incidents.CountActiveAsync(cancellationToken);
        _telemetry.RecordActiveIncidents(activeCount);
        _logger.LogInformation(
            "Health analysis complete. Devices evaluated={DeviceCount}, incidents opened={Opened}, activeIncidents={Active}",
            snapshots.Count,
            opened,
            activeCount);
    }

    private async Task<IReadOnlyList<DeviceTrendSnapshot>> EvaluateDeviceTrendsAsync(
        CancellationToken cancellationToken)
    {
        var cutoff = DateTime.UtcNow.AddMinutes(-_settings.LookbackMinutes);

        var pipeline = new[]
        {
            new BsonDocument("$match", new BsonDocument(
                "timestamp",
                new BsonDocument("$gte", cutoff))),
            new BsonDocument("$setWindowFields", new BsonDocument
            {
                { "partitionBy", "$metadata.deviceId" },
                { "sortBy", new BsonDocument("timestamp", 1) },
                {
                    "output", new BsonDocument
                    {
                        { "gpuTemp1m", WindowAvg("$gpuTemperature", -1) },
                        { "gpuTemp5m", WindowAvg("$gpuTemperature", -5) },
                        { "latency1m", WindowAvg("$inferenceLatencyMs", -1) },
                        { "latency5m", WindowAvg("$inferenceLatencyMs", -5) },
                        { "fps1m", WindowAvg("$fps", -1) },
                        { "packetLoss1m", WindowAvg("$packetLossPct", -1) },
                        { "networkLatency1m", WindowAvg("$networkLatencyMs", -1) },
                        { "dropped1m", WindowAvg("$droppedFrames", -1) }
                    }
                }
            }),
            new BsonDocument("$sort", new BsonDocument("timestamp", -1)),
            new BsonDocument("$group", new BsonDocument
            {
                { "_id", "$metadata.deviceId" },
                { "site", new BsonDocument("$first", "$metadata.site") },
                { "line", new BsonDocument("$first", "$metadata.line") },
                { "timestamp", new BsonDocument("$first", "$timestamp") },
                { "gpuTemp1m", new BsonDocument("$first", "$gpuTemp1m") },
                { "gpuTemp5m", new BsonDocument("$first", "$gpuTemp5m") },
                { "latency1m", new BsonDocument("$first", "$latency1m") },
                { "latency5m", new BsonDocument("$first", "$latency5m") },
                { "fps1m", new BsonDocument("$first", "$fps1m") },
                { "packetLoss1m", new BsonDocument("$first", "$packetLoss1m") },
                { "networkLatency1m", new BsonDocument("$first", "$networkLatency1m") },
                { "dropped1m", new BsonDocument("$first", "$dropped1m") },
                { "profile", new BsonDocument("$first", "$profile") },
                { "status", new BsonDocument("$first", "$status") }
            })
        };

        var results = await _mongo.Telemetry
            .Aggregate<BsonDocument>(pipeline, cancellationToken: cancellationToken)
            .ToListAsync(cancellationToken);

        return results.Select(DeviceTrendSnapshot.FromDocument).ToList();
    }

    private bool IsThermalIncident(DeviceTrendSnapshot snapshot)
    {
        // Network evidence must stay calm; otherwise prefer a network incident path later.
        if (snapshot.PacketLoss1m >= _settings.PacketLossMaxPct || snapshot.NetworkLatency1m >= 80.0)
        {
            return false;
        }

        var temperatureHot =
            snapshot.GpuTemp1m >= _settings.GpuTemperatureThresholdC ||
            snapshot.GpuTemp1m - snapshot.GpuTemp5m >= _settings.GpuTemperatureRiseC;

        var inferenceDegraded =
            snapshot.Latency1m >= _settings.InferenceLatencyThresholdMs ||
            snapshot.Latency1m - snapshot.Latency5m >= _settings.InferenceLatencyRiseMs ||
            snapshot.Fps1m <= _settings.FpsFloor;

        return temperatureHot && inferenceDegraded;
    }

    private static BsonDocument WindowAvg(string fieldPath, int rangeStartMinutes) =>
        new()
        {
            { "$avg", fieldPath },
            {
                "window", new BsonDocument
                {
                    { "range", new BsonArray { rangeStartMinutes, 0 } },
                    { "unit", "minute" }
                }
            }
        };

    private static IncidentRecord CreateIncident(DeviceTrendSnapshot snapshot)
    {
        // Note: the 5-minute rolling window includes the latest minute (trailing window),
        // so the delta is "recent average vs longer trailing average", not a disjoint prior window.
        var rootCause =
            $"Thermal throttling suspected: GPU 1m avg {snapshot.GpuTemp1m:F1}C vs trailing 5m {snapshot.GpuTemp5m:F1}C; " +
            $"latency 1m {snapshot.Latency1m:F1}ms vs trailing 5m {snapshot.Latency5m:F1}ms; " +
            $"packet loss {snapshot.PacketLoss1m:F2}%, network latency {snapshot.NetworkLatency1m:F1}ms " +
            "(network path looks calm relative to thermal/inference degradation).";

        return new IncidentRecord(
            Id: $"inc-thermal-{snapshot.DeviceId}-{DateTimeOffset.UtcNow:yyyyMMddHHmmss}",
            DeviceId: snapshot.DeviceId,
            Type: IncidentType.ThermalThrottling,
            Severity: IncidentSeverity.High,
            Status: IncidentStatus.Open,
            DetectedAt: DateTimeOffset.UtcNow,
            ResolvedAt: null,
            Evidence: new IncidentEvidence(
                snapshot.GpuTemp1m,
                snapshot.Latency1m,
                snapshot.Fps1m,
                (int)Math.Round(snapshot.Dropped1m)),
            RootCause: rootCause,
            RemediationId: null);
    }

    private sealed record DeviceTrendSnapshot(
        string DeviceId,
        string Site,
        string Line,
        DateTime Timestamp,
        double GpuTemp1m,
        double GpuTemp5m,
        double Latency1m,
        double Latency5m,
        double Fps1m,
        double PacketLoss1m,
        double NetworkLatency1m,
        double Dropped1m,
        string Profile,
        string Status)
    {
        public static DeviceTrendSnapshot FromDocument(BsonDocument document) =>
            new(
                document["_id"].AsString,
                document.GetValue("site", "").AsString,
                document.GetValue("line", "").AsString,
                document.GetValue("timestamp").ToUniversalTime(),
                document.GetValue("gpuTemp1m", 0).ToDouble(),
                document.GetValue("gpuTemp5m", 0).ToDouble(),
                document.GetValue("latency1m", 0).ToDouble(),
                document.GetValue("latency5m", 0).ToDouble(),
                document.GetValue("fps1m", 0).ToDouble(),
                document.GetValue("packetLoss1m", 0).ToDouble(),
                document.GetValue("networkLatency1m", 0).ToDouble(),
                document.GetValue("dropped1m", 0).ToDouble(),
                document.GetValue("profile", "full").AsString,
                document.GetValue("status", "healthy").AsString);
    }
}
