using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;
using EdgeGuard.Shared.Persistence;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEdgeGuardConfiguration(builder.Configuration);
builder.Services.AddEdgeGuardMongo();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var mongo = scope.ServiceProvider.GetRequiredService<EdgeGuardMongoContext>();
    await mongo.EnsureInitializedAsync(CancellationToken.None);
}

app.Logger.LogInformation("Telemetry API ready. POST /telemetry writes to MongoDB time-series.");

app.MapGet("/health", async (EdgeGuardMongoContext mongo, CancellationToken cancellationToken) =>
{
    var mongoOk = await mongo.CanPingAsync(cancellationToken);
    var status = mongoOk ? "healthy" : "degraded";
    return Results.Ok(new HealthResponse(status, "telemetry-api", false, mongoOk));
});

app.MapPost("/telemetry", async (
    TelemetryIngestRequest request,
    ITelemetryRepository telemetryRepository,
    IDeviceRepository deviceRepository,
    IOperationalTelemetry operationalTelemetry,
    ILogger<Program> logger,
    CancellationToken cancellationToken) =>
{
    using var activity = TraceSources.ActivitySource.StartActivity(TraceSources.IngestTelemetry);
    activity?.SetTag("device.id", request.DeviceId);
    activity?.SetTag("site", request.Site);
    activity?.SetTag("line", request.Line);

    try
    {
        var reading = request.ToReading();

        using (TraceSources.ActivitySource.StartActivity(TraceSources.InsertTelemetry))
        {
            await telemetryRepository.InsertAsync(reading, cancellationToken);
        }

        await UpsertDeviceFromTelemetryAsync(deviceRepository, reading, cancellationToken);
        operationalTelemetry.RecordDeviceSample(reading);

        logger.LogInformation(
            "Ingested telemetry device={DeviceId} site={Site} line={Line} gpuTemp={GpuTemperature:F1} fps={Fps:F1} latencyMs={Latency:F1} profile={Profile}",
            reading.Metadata.DeviceId,
            reading.Metadata.Site,
            reading.Metadata.Line,
            reading.GpuTemperature,
            reading.Fps,
            reading.InferenceLatencyMs,
            DomainMappings.FormatProfile(reading.Profile));

        return Results.Accepted(value: new TelemetryAcceptedResponse(
            reading.Metadata.DeviceId,
            reading.Timestamp,
            DomainMappings.FormatProfile(reading.Profile),
            DomainMappings.FormatStatus(reading.Status)));
    }
    catch (ArgumentException ex)
    {
        return Results.BadRequest(new { error = ex.Message });
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Telemetry ingest failed for device {DeviceId}", request.DeviceId);
        return Results.Problem(
            title: "Telemetry ingest failed",
            detail: ex.Message,
            statusCode: StatusCodes.Status500InternalServerError);
    }
});

app.Run();

static async Task UpsertDeviceFromTelemetryAsync(
    IDeviceRepository deviceRepository,
    TelemetryReading reading,
    CancellationToken cancellationToken)
{
    var existing = await deviceRepository.GetAsync(reading.Metadata.DeviceId, cancellationToken);
    if (existing is null)
    {
        var created = new DeviceRecord(
            reading.Metadata.DeviceId,
            $"Edge Camera {reading.Metadata.DeviceId}",
            reading.Metadata.Site,
            reading.Metadata.Line,
            "edge-camera",
            new HardwareInfo("synthetic-cpu", "synthetic-gpu"),
            reading.Profile,
            reading.Status,
            DateTimeOffset.UtcNow);
        await deviceRepository.UpsertAsync(created, cancellationToken);
        return;
    }

    if (existing.Profile != reading.Profile || existing.Status != reading.Status)
    {
        var updated = existing with
        {
            Profile = reading.Profile,
            Status = reading.Status
        };
        await deviceRepository.UpsertAsync(updated, cancellationToken);
    }
}

internal sealed record HealthResponse(string Status, string Service, bool Scaffold, bool MongoOk);

internal sealed record TelemetryAcceptedResponse(
    string DeviceId,
    DateTimeOffset Timestamp,
    string Profile,
    string Status);

public partial class Program;
