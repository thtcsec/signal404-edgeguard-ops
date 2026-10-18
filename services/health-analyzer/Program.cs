using EdgeGuard.HealthAnalyzer;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Observability;
using EdgeGuard.Shared.Persistence;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddEdgeGuardConfiguration(builder.Configuration);
builder.Services.AddEdgeGuardObservability(builder.Configuration);
builder.Services.AddEdgeGuardMongo();
builder.Services.AddSingleton<IFleetHealthAnalyzer, FleetThermalHealthAnalyzer>();
builder.Services.AddHostedService<HealthAnalyzerWorker>();
builder.Logging.AddEdgeGuardLogging(builder.Configuration);

var host = builder.Build();

using (var scope = host.Services.CreateScope())
{
    var mongo = scope.ServiceProvider.GetRequiredService<EdgeGuardMongoContext>();
    await mongo.EnsureInitializedAsync(CancellationToken.None);
}

await host.RunAsync();
