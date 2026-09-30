using EdgeGuard.Shared.Contracts;

namespace EdgeGuard.ResponseWorker;

public sealed class RemediationWorker : BackgroundService
{
    private readonly ILogger<RemediationWorker> _logger;
    private readonly IRemediationExecutor _executor;

    public RemediationWorker(ILogger<RemediationWorker> logger, IRemediationExecutor executor)
    {
        _logger = logger;
        _executor = executor;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation(
            "Response worker pre-hackathon scaffold is idle. Registered executor: {Executor}. Automatic remediation is not implemented.",
            _executor.GetType().Name);

        // TODO(build-window): watch the incidents collection with a MongoDB change stream,
        // call IRemediationExecutor for new OPEN incidents, switch the simulated device
        // to a safe profile, and move the incident through MITIGATING, RECOVERING, and RESOLVED.
        // Do not call the placeholder here: it throws NotSupportedException.

        try
        {
            await Task.Delay(Timeout.Infinite, stoppingToken);
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
        }
    }
}
