namespace EdgeGuard.Shared.Domain;

public sealed record RemediationActionRecord(
    string Id,
    string IncidentId,
    string DeviceId,
    RemediationActionType ActionType,
    RemediationState State,
    DateTimeOffset RequestedAt,
    DateTimeOffset? CompletedAt);
