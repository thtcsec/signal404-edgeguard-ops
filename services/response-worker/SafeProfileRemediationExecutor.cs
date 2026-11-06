using System.Collections.Concurrent;
using System.Diagnostics;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;
using Microsoft.Extensions.Options;

namespace EdgeGuard.ResponseWorker;

/// <summary>
/// Polls MongoDB for open/mitigating/recovering incidents.
/// Standalone Compose MongoDB has no replica set, so change streams are not used.
/// Correlates work with device_id / incident_id / action_id tags (no cross-process trace propagation claimed).
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
            using var incidentActivity = TraceSources.ActivitySource.StartActivity("Remediation.incident");
            incidentActivity?.SetTag("device.id", incident.DeviceId);
            incidentActivity?.SetTag("incident.id", incident.Id);
            incidentActivity?.SetTag("incident.status", incident.Status.ToString());

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
                "Skipping remediation incident_id={IncidentId} device_id={DeviceId}: device not found yet.",
                incident.Id,
                incident.DeviceId);
            return;
        }

        // Stable per incident so a partial failure can safely resume on the next poll.
        var actionId = $"act-safe-{incident.Id}";
        var action = await _actions.GetAsync(actionId, cancellationToken) ?? new RemediationActionRecord(
            Id: actionId,
            IncidentId: incident.Id,
            DeviceId: incident.DeviceId,
            ActionType: RemediationActionType.SwitchToSafeProfile,
            State: RemediationState.Requested,
            RequestedAt: DateTimeOffset.UtcNow,
            CompletedAt: null);

        Activity.Current?.SetTag("action.id", action.Id);

        await _actions.InsertAsync(action, cancellationToken);
        await _devices.SetCommandedProfileAsync(incident.DeviceId, DeviceProfile.Safe, cancellationToken);

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
            "Remediation applied incident_id={IncidentId} device_id={DeviceId} action_id={ActionId} commanded_profile=safe",
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

        // Evidence must be reported/applied safe in telemetry — commanded alone is not enough.
        if (recent.Count == 0 || recent.All(x => x.Profile != DeviceProfile.Safe))
        {
            _logger.LogDebug(
                "Waiting for reported_profile=safe telemetry incident_id={IncidentId} device_id={DeviceId}",
                incident.Id,
                incident.DeviceId);
            return;
        }

        var updated = incident with { Status = IncidentStatus.Recovering };
        await _incidents.UpdateAsync(updated, cancellationToken);
        _recoveringSince[incident.Id] = DateTimeOffset.UtcNow;

        _logger.LogInformation(
            "Incident entered RECOVERING incident_id={IncidentId} device_id={DeviceId} observation_seconds={Seconds}",
            incident.Id,
            incident.DeviceId,
            _settings.ObservationSeconds);
    }

    private async Task TryResolveAsync(IncidentRecord incident, CancellationToken cancellationToken)
    {
        var since = _recoveringSince.GetOrAdd(incident.Id, DateTimeOffset.UtcNow);
        var device = await _devices.GetAsync(incident.DeviceId, cancellationToken);
        if (device is null)
        {
            return;
        }

        var recent = await _telemetry.GetRecentAsync(
            incident.DeviceId,
            TimeSpan.FromSeconds(_settings.RecentTelemetrySeconds),
            cancellationToken);

        var evaluation = RecoveryEvidence.Evaluate(
            recent,
            device.Profile,
            since,
            DateTimeOffset.UtcNow,
            _settings.ObservationSeconds,
            _settings.MaxTelemetryStalenessSeconds,
            _settings.MaxSampleGapSeconds,
            _settings.MinHealthySamples,
            _settings.RecoveredGpuTemperatureMaxC,
            _settings.RecoveredInferenceLatencyMaxMs,
            _settings.RecoveredFpsMin);

        if (evaluation.ShouldResetObservation)
        {
            _recoveringSince[incident.Id] = DateTimeOffset.UtcNow;
            _logger.LogInformation(
                "Observation reset incident_id={IncidentId} device_id={DeviceId} reason={Reason}",
                incident.Id,
                incident.DeviceId,
                evaluation.Reason);
            return;
        }

        if (!evaluation.IsRecovered)
        {
            _logger.LogDebug(
                "Still recovering incident_id={IncidentId} device_id={DeviceId} reason={Reason}",
                incident.Id,
                incident.DeviceId,
                evaluation.Reason);
            return;
        }

        // Do not publish RESOLVED until the linked action is durably VERIFIED.
        // A failed action write leaves RECOVERING so the next poll can retry.
        var action = incident.RemediationId is null
            ? null
            : await _actions.GetAsync(incident.RemediationId, cancellationToken);
        if (action is null || action.IncidentId != incident.Id || action.DeviceId != incident.DeviceId)
        {
            _logger.LogWarning("Cannot resolve incident_id={IncidentId}: linked remediation missing or mismatched.", incident.Id);
            return;
        }

        await _actions.UpdateAsync(action with
        {
            State = RemediationState.Verified,
            CompletedAt = action.CompletedAt ?? DateTimeOffset.UtcNow
        }, cancellationToken);
        Activity.Current?.SetTag("action.id", action.Id);

        var resolved = incident with
        {
            Status = IncidentStatus.Resolved,
            ResolvedAt = DateTimeOffset.UtcNow
        };
        await _incidents.UpdateAsync(resolved, cancellationToken);

        _recoveringSince.TryRemove(incident.Id, out _);

        _logger.LogWarning(
            "Incident RESOLVED incident_id={IncidentId} device_id={DeviceId} action_id={ActionId} reason={Reason}",
            incident.Id,
            incident.DeviceId,
            incident.RemediationId,
            evaluation.Reason);
    }
}
