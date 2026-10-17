using System.Collections.Concurrent;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;
using Microsoft.Extensions.Options;

namespace EdgeGuard.ResponseWorker;

/// <summary>
/// Polls MongoDB for open/mitigating/recovering incidents.
/// Standalone Compose MongoDB has no replica set, so change streams are not used.
/// Switches devices to the safe profile, observes recovery telemetry, then resolves.
/// </summary>
public sealed class SafeProfileRemediationExecutor : IRemediationExecutor
{
    private readonly IIncidentRepository _incidents;
    private readonly IDeviceRepository _devices;
    private readonly ITelemetryRepository _telemetry;
    private readonly IRemediationActionRepository _actions;
    private readonly IOperationalTelemetry _metrics;
    private readonly RemediationSettings _settings;
    private readonly ILogger<SafeProfileRemediationExecutor> _logger;
    private readonly ConcurrentDictionary<string, DateTimeOffset> _recoveringSince = new();

    public SafeProfileRemediationExecutor(
        IIncidentRepository incidents,
        IDeviceRepository devices,
        ITelemetryRepository telemetry,
        IRemediationActionRepository actions,
        IOperationalTelemetry metrics,
        IOptions<RemediationSettings> settings,
        ILogger<SafeProfileRemediationExecutor> logger)
    {
        _incidents = incidents;
        _devices = devices;
        _telemetry = telemetry;
        _actions = actions;
        _metrics = metrics;
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task ProcessAsync(CancellationToken cancellationToken)
    {
        using var activity = TraceSources.ActivitySource.StartActivity(TraceSources.ExecuteRemediation);

        var active = await _incidents.ListByStatusesAsync(
            [
                IncidentStatus.Open,
                IncidentStatus.Investigating,
                IncidentStatus.Mitigating,
                IncidentStatus.Recovering
            ],
            cancellationToken);

        foreach (var incident in active)
        {
            switch (incident.Status)
            {
                case IncidentStatus.Open:
                case IncidentStatus.Investigating:
                    await BeginMitigationAsync(incident, cancellationToken);
                    break;
                case IncidentStatus.Mitigating:
                    await PromoteToRecoveringAsync(incident, cancellationToken);
                    break;
                case IncidentStatus.Recovering:
                    await TryResolveAsync(incident, cancellationToken);
                    break;
            }
        }

        var activeCount = await _incidents.CountActiveAsync(cancellationToken);
        _metrics.RecordActiveIncidents(activeCount);
    }

    private async Task BeginMitigationAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        if (incident.RemediationId is not null)
        {
            return;
        }

        var device = await _devices.GetAsync(incident.DeviceId, cancellationToken);
        if (device is null)
        {
            _logger.LogWarning(
                "Skipping remediation for {IncidentId}: device {DeviceId} not found yet.",
                incident.Id,
                incident.DeviceId);
            return;
        }

        var action = new RemediationActionRecord(
            Id: $"act-safe-{incident.DeviceId}-{DateTimeOffset.UtcNow:yyyyMMddHHmmss}",
            IncidentId: incident.Id,
            DeviceId: incident.DeviceId,
            ActionType: RemediationActionType.SwitchToSafeProfile,
            State: RemediationState.Requested,
            RequestedAt: DateTimeOffset.UtcNow,
            CompletedAt: null);

        await _actions.InsertAsync(action, cancellationToken);
        await _devices.SetProfileAsync(incident.DeviceId, DeviceProfile.Safe, cancellationToken);

        var applied = action with { State = RemediationState.Applied };
        await _actions.UpdateAsync(applied, cancellationToken);

        var updated = incident with
        {
            Status = IncidentStatus.Mitigating,
            RemediationId = action.Id
        };
        await _incidents.UpdateAsync(updated, cancellationToken);
        _metrics.RecordRemediation(RemediationActionType.SwitchToSafeProfile);

        _logger.LogWarning(
            "Remediation applied for {IncidentId}: device {DeviceId} profile -> safe (action {ActionId})",
            incident.Id,
            incident.DeviceId,
            action.Id);
    }

    private async Task PromoteToRecoveringAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        var device = await _devices.GetAsync(incident.DeviceId, cancellationToken);
        if (device is null || device.Profile != DeviceProfile.Safe)
        {
            return;
        }

        var recent = await _telemetry.GetRecentAsync(
            incident.DeviceId,
            TimeSpan.FromSeconds(_settings.RecentTelemetrySeconds),
            cancellationToken);

        if (recent.Count == 0 || recent.All(x => x.Profile != DeviceProfile.Safe))
        {
            return;
        }

        var updated = incident with { Status = IncidentStatus.Recovering };
        await _incidents.UpdateAsync(updated, cancellationToken);
        _recoveringSince[incident.Id] = DateTimeOffset.UtcNow;

        _logger.LogInformation(
            "Incident {IncidentId} entered RECOVERING; observing at least {Seconds}s before resolve.",
            incident.Id,
            _settings.ObservationSeconds);
    }

    private async Task TryResolveAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        var since = _recoveringSince.GetOrAdd(incident.Id, DateTimeOffset.UtcNow);
        if (DateTimeOffset.UtcNow - since < TimeSpan.FromSeconds(_settings.ObservationSeconds))
        {
            return;
        }

        var recent = await _telemetry.GetRecentAsync(
            incident.DeviceId,
            TimeSpan.FromSeconds(_settings.RecentTelemetrySeconds),
            cancellationToken);

        if (!IsRecovered(recent))
        {
            _logger.LogDebug(
                "Incident {IncidentId} still recovering. Recent samples={Count}",
                incident.Id,
                recent.Count);
            return;
        }

        var resolved = incident with
        {
            Status = IncidentStatus.Resolved,
            ResolvedAt = DateTimeOffset.UtcNow
        };
        await _incidents.UpdateAsync(resolved, cancellationToken);

        if (incident.RemediationId is not null)
        {
            var action = await _actions.GetAsync(incident.RemediationId, cancellationToken);
            if (action is not null)
            {
                var verified = action with
                {
                    State = RemediationState.Verified,
                    CompletedAt = DateTimeOffset.UtcNow
                };
                await _actions.UpdateAsync(verified, cancellationToken);
            }
        }

        _recoveringSince.TryRemove(incident.Id, out _);

        _logger.LogWarning(
            "Incident {IncidentId} RESOLVED after safe-profile recovery for {DeviceId}.",
            incident.Id,
            incident.DeviceId);
    }

    private bool IsRecovered(IReadOnlyList<TelemetryReading> recent)
    {
        if (recent.Count == 0)
        {
            return false;
        }

        var safeSamples = recent.Where(x => x.Profile == DeviceProfile.Safe).ToList();
        if (safeSamples.Count == 0)
        {
            return false;
        }

        var avgGpu = safeSamples.Average(x => x.GpuTemperature);
        var avgLatency = safeSamples.Average(x => x.InferenceLatencyMs);
        var avgFps = safeSamples.Average(x => x.Fps);

        return avgGpu <= _settings.RecoveredGpuTemperatureMaxC
            && avgLatency <= _settings.RecoveredInferenceLatencyMaxMs
            && avgFps >= _settings.RecoveredFpsMin
            && safeSamples.All(x => x.Status == DeviceStatus.Healthy);
    }
}
