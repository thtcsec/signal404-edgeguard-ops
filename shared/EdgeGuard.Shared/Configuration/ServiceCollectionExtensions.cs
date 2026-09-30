using EdgeGuard.Shared.Observability;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EdgeGuard.Shared.Configuration;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddEdgeGuardConfiguration(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.Configure<MongoDbSettings>(configuration.GetSection(MongoDbSettings.SectionName));
        services.Configure<ObservabilitySettings>(configuration.GetSection(ObservabilitySettings.SectionName));
        services.AddSingleton<IOperationalTelemetry, NoOpOperationalTelemetry>();
        return services;
    }
}
