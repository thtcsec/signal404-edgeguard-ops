using EdgeGuard.ResponseWorker;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Placeholders;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddEdgeGuardConfiguration(builder.Configuration);
builder.Services.AddSingleton<IIncidentRepository, UnimplementedIncidentRepository>();
builder.Services.AddSingleton<IRemediationExecutor, UnimplementedRemediationExecutor>();
builder.Services.AddHostedService<RemediationWorker>();

var host = builder.Build();
await host.RunAsync();
