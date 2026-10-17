using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using Microsoft.Extensions.Options;

namespace EdgeGuard.ResponseWorker;

public sealed class RemediationWorker : BackgroundService
{
    private readonly ILogger<RemediationWorker> _logger;
    private readonly IRemediationExecutor _executor;
    private readonly RemediationSettings _settings;

    public RemediationWorker(
        ILogger<RemediationWorker> logger,
        IRemediationExecutor executor,
        IOptions<RemediationSettings> settings)
    {
        _logger = logger;
        _executor = executor;
        _settings = settings.Value;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var interval = TimeSpan.FromSeconds(Math.Max(3, _settings.PollIntervalSeconds));
        _logger.LogInformation(
            "Response worker started. PollInterval={IntervalSeconds}s Executor={Executor}",
            interval.TotalSeconds,
            _executor.GetType().Name);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await _executor.ProcessAsync(stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Remediation cycle failed.");
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
