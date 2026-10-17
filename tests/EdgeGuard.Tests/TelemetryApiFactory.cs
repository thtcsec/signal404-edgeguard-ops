using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Persistence;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;
using MongoDB.Driver;

namespace EdgeGuard.Tests;

public sealed class TelemetryApiFactory : WebApplicationFactory<Program>
{
    private readonly string _databaseName = $"edgeguard_test_{Guid.NewGuid():N}";

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Development");
        builder.ConfigureServices(services =>
        {
            services.RemoveAll<EdgeGuardMongoContext>();
            services.RemoveAll<IDeviceRepository>();
            services.RemoveAll<ITelemetryRepository>();
            services.RemoveAll<IIncidentRepository>();
            services.RemoveAll<IRemediationActionRepository>();

            services.PostConfigure<MongoDbSettings>(settings =>
            {
                settings.ConnectionString = Environment.GetEnvironmentVariable("EDGEGUARD_TEST_MONGODB")
                    ?? "mongodb://localhost:27017";
                settings.DatabaseName = _databaseName;
            });

            services.AddEdgeGuardMongo();
        });
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            try
            {
                var settings = Services.GetRequiredService<IOptions<MongoDbSettings>>().Value;
                var client = new MongoClient(settings.ConnectionString);
                client.DropDatabase(_databaseName);
            }
            catch
            {
                // Test cleanup best-effort when MongoDB is unavailable.
            }
        }

        base.Dispose(disposing);
    }
}
