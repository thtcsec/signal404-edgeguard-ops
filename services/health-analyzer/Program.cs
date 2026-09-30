using EdgeGuard.HealthAnalyzer;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Placeholders;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddEdgeGuardConfiguration(builder.Configuration);
builder.Services.AddSingleton<IIncidentRepository, UnimplementedIncidentRepository>();
builder.Services.AddSingleton<IFleetHealthAnalyzer, UnimplementedFleetHealthAnalyzer>();
builder.Services.AddHostedService<HealthAnalyzerWorker>();

var host = builder.Build();
await host.RunAsync();
