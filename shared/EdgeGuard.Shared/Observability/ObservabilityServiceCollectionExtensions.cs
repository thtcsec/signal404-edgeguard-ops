using EdgeGuard.Shared.Configuration;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Console;
using Microsoft.Extensions.Options;

namespace EdgeGuard.Shared.Observability;

public static class ObservabilityServiceCollectionExtensions
{
    public static IServiceCollection AddEdgeGuardObservability(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.Configure<ObservabilitySettings>(configuration.GetSection(ObservabilitySettings.SectionName));

        // Replace the default NoOp registration from AddEdgeGuardConfiguration when Datadog is enabled.
        services.RemoveAll<IOperationalTelemetry>();
        services.AddSingleton<IOperationalTelemetry>(sp =>
        {
            var settings = sp.GetRequiredService<IOptions<ObservabilitySettings>>().Value;
            if (!settings.DatadogEnabled)
            {
                return new NoOpOperationalTelemetry();
            }

            return new DogStatsDOperationalTelemetry(settings.AgentHost, settings.DogStatsDPort);
        });

        // Load Datadog.Trace so the automatic tracer can discover EdgeGuard.Ops ActivitySource
        // when DD_TRACE_OTEL_ENABLED=true / agent APM is available. Safe no-op if agent absent.
        _ = typeof(Datadog.Trace.Tracer);

        return services;
    }

    public static ILoggingBuilder AddEdgeGuardJsonConsole(this ILoggingBuilder logging)
    {
        logging.ClearProviders();
        logging.AddJsonConsole(options =>
        {
            options.IncludeScopes = true;
            options.TimestampFormat = "O";
            options.JsonWriterOptions = new System.Text.Json.JsonWriterOptions
            {
                Indented = false
            };
        });
        return logging;
    }
}
