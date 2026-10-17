using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using Microsoft.Extensions.Options;

namespace EdgeGuard.HealthAnalyzer;

public sealed class HealthAnalyzerWorker : BackgroundService
{
    private readonly ILogger<HealthAnalyzerWorker> _logger;
    private readonly IFleetHealthAnalyzer _analyzer;
    private readonly AnalyzerSettings _settings;

    public HealthAnalyzerWorker(
        ILogger<HealthAnalyzerWorker> logger,
        IFleetHealthAnalyzer analyzer,
        IOptions<AnalyzerSettings> settings)
    {
        _logger = logger;
        _analyzer = analyzer;
        _settings = settings.Value;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var interval = TimeSpan.FromSeconds(Math.Max(5, _settings.IntervalSeconds));
        _logger.LogInformation(
            "Health analyzer started. Interval={IntervalSeconds}s Analyzer={Analyzer}",
            interval.TotalSeconds,
            _analyzer.GetType().Name);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await _analyzer.AnalyzeAsync(stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Health analysis cycle failed.");
            }

            try
            {
                await Task.Delay(interval, stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
        }
    }
}
