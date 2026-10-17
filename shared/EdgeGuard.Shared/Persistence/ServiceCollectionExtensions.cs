using EdgeGuard.Shared.Contracts;
using Microsoft.Extensions.DependencyInjection;

namespace EdgeGuard.Shared.Persistence;

public static class PersistenceServiceCollectionExtensions
{
    public static IServiceCollection AddEdgeGuardMongo(this IServiceCollection services)
    {
        services.AddSingleton<EdgeGuardMongoContext>();
        services.AddSingleton<IDeviceRepository, MongoDeviceRepository>();
        services.AddSingleton<ITelemetryRepository, MongoTelemetryRepository>();
        services.AddSingleton<IIncidentRepository, MongoIncidentRepository>();
        services.AddSingleton<IRemediationActionRepository, MongoRemediationActionRepository>();
        return services;
    }
}
