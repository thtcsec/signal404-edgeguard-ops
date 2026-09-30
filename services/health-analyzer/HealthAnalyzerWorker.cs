using EdgeGuard.Shared.Contracts;

namespace EdgeGuard.HealthAnalyzer;

public sealed class HealthAnalyzerWorker : BackgroundService
{
    private readonly ILogger<HealthAnalyzerWorker> _logger;
    private readonly IFleetHealthAnalyzer _analyzer;

    public HealthAnalyzerWorker(ILogger<HealthAnalyzerWorker> logger, IFleetHealthAnalyzer analyzer)
    {
        _logger = logger;
        _analyzer = analyzer;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation(
            "Health analyzer pre-hackathon scaffold is idle. Registered analyzer: {Analyzer}. Trend detection is not implemented.",
            _analyzer.GetType().Name);

        // TODO(build-window): call IFleetHealthAnalyzer.AnalyzeAsync on an interval.
        // Use an aggregation pipeline with $setWindowFields to compare the current
        // 1-minute average against the previous 5-minute rolling average, then insert
        // an incident when degradation is confirmed. Do not call the placeholder here:
        // it throws NotSupportedException.

        try
        {
            await Task.Delay(Timeout.Infinite, stoppingToken);
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
        }
    }
}
