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

            return new DogStatsDOperationalTelemetry(
                settings.AgentHost,
                settings.DogStatsDPort,
                settings.EnvironmentName);
        });

        return services;
    }

    public static ILoggingBuilder AddEdgeGuardLogging(
        this ILoggingBuilder logging,
        IConfiguration configuration)
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

        var settings = configuration.GetSection(ObservabilitySettings.SectionName).Get<ObservabilitySettings>()
            ?? new ObservabilitySettings();

        if (settings.DatadogEnabled && !string.IsNullOrWhiteSpace(settings.LogDirectory))
        {
            var directory = Path.GetFullPath(settings.LogDirectory);
            Directory.CreateDirectory(directory);
            var filePath = Path.Combine(directory, $"{SanitizeFileName(settings.ServiceName)}.log");
            logging.AddProvider(new JsonFileLoggerProvider(filePath));
        }

        return logging;
    }

    private static string SanitizeFileName(string serviceName)
    {
        var invalid = Path.GetInvalidFileNameChars();
        var chars = serviceName.Select(ch => invalid.Contains(ch) ? '_' : ch).ToArray();
        return new string(chars);
    }
}
