using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Placeholders;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEdgeGuardConfiguration(builder.Configuration);
builder.Services.AddSingleton<IDeviceRepository, UnimplementedDeviceRepository>();
builder.Services.AddSingleton<ITelemetryRepository, UnimplementedTelemetryRepository>();

var app = builder.Build();

app.Logger.LogInformation(
    "Telemetry API pre-hackathon scaffold started. POST /telemetry returns 501.");

app.MapGet("/health", () => Results.Ok(new HealthResponse("healthy", "telemetry-api", true)));

// TODO(build-window): bind TelemetryIngestRequest, validate it, start
// TraceSources.ActivitySource activities named TraceSources.IngestTelemetry and
// TraceSources.InsertTelemetry, and insert into the telemetry time-series collection.
app.MapPost("/telemetry", () => Results.Problem(
    title: "Telemetry ingestion is not implemented",
    detail: "Pre-hackathon scaffold. Implement MongoDB Time Series ingestion during 2026-10-10 to 2026-10-24.",
    statusCode: StatusCodes.Status501NotImplemented));

app.Run();

internal sealed record HealthResponse(string Status, string Service, bool Scaffold);

public partial class Program;
