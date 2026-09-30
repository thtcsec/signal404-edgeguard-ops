namespace EdgeGuard.Shared.Domain;

public enum DeviceProfile
{
    Full,
    Reduced,
    Safe
}

public enum DeviceStatus
{
    Healthy,
    Degraded,
    Offline
}

public enum IncidentStatus
{
    Open,
    Investigating,
    Mitigating,
    Recovering,
    Resolved
}

public enum IncidentType
{
    ThermalThrottling,
    NetworkDegradation,
    MemoryPressure
}

public enum IncidentSeverity
{
    Low,
    Medium,
    High
}

public enum RemediationActionType
{
    SwitchToSafeProfile,
    ReduceInferenceRate,
    RestartInferenceService
}

public enum RemediationState
{
    Requested,
    Applied,
    Verified,
    Failed
}

public enum SimulatorScenario
{
    Normal,
    ThermalThrottle,
    NetworkDegradation,
    MemoryPressure
}
