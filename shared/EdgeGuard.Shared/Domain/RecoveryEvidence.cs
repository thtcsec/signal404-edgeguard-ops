namespace EdgeGuard.Shared.Domain;

public sealed record RecoveryEvaluation(
    bool IsRecovered,
    bool ShouldResetObservation,
    string Reason);

/// <summary>
/// Evaluates continuous recovery evidence using reported telemetry profiles,
/// never treating commanded profile alone as proof the device applied safe mode.
/// </summary>
public static class RecoveryEvidence
{
    public static RecoveryEvaluation Evaluate(
        IReadOnlyList<TelemetryReading> recent,
        DeviceProfile commandedProfile,
        DateTimeOffset observationStartedAt,
        DateTimeOffset now,
        int observationSeconds,
        int maxStalenessSeconds,
        int maxSampleGapSeconds,
        int minHealthySamples,
        double recoveredGpuMaxC,
        double recoveredLatencyMaxMs,
        double recoveredFpsMin)
    {
        if (commandedProfile != DeviceProfile.Safe)
        {
            return new RecoveryEvaluation(false, false, "Commanded profile is not safe yet.");
        }

        var windowStart = observationStartedAt;
        var inWindow = recent
            .Where(x => x.Timestamp >= windowStart)
            .OrderBy(x => x.Timestamp)
            .ToList();

        if (inWindow.Count == 0)
        {
            return new RecoveryEvaluation(false, true, "No telemetry received since observation started.");
        }

        if (inWindow.Any(x => x.Timestamp > now))
        {
            return new RecoveryEvaluation(false, true, "Future-dated telemetry cannot prove recovery.");
        }

        var latest = inWindow[^1];
        if (now - latest.Timestamp > TimeSpan.FromSeconds(maxStalenessSeconds))
        {
            return new RecoveryEvaluation(
                false,
                true,
                $"Telemetry stale: latest sample age {(now - latest.Timestamp).TotalSeconds:F1}s.");
        }

        if (inWindow[0].Timestamp - windowStart > TimeSpan.FromSeconds(maxSampleGapSeconds))
        {
            return new RecoveryEvaluation(
                false,
                true,
                "Gap between observation start and first sample exceeded threshold.");
        }

        for (var i = 1; i < inWindow.Count; i++)
        {
            var gap = inWindow[i].Timestamp - inWindow[i - 1].Timestamp;
            if (gap > TimeSpan.FromSeconds(maxSampleGapSeconds))
            {
                return new RecoveryEvaluation(
                    false,
                    true,
                    $"Telemetry gap of {gap.TotalSeconds:F1}s broke continuous evidence.");
            }
        }

        // Reported profile must show the device applied safe — commanded-only is insufficient.
        var healthy = inWindow
            .Where(x =>
                x.Profile == DeviceProfile.Safe &&
                x.Status == DeviceStatus.Healthy &&
                x.GpuTemperature <= recoveredGpuMaxC &&
                x.InferenceLatencyMs <= recoveredLatencyMaxMs &&
                x.Fps >= recoveredFpsMin)
            .ToList();

        if (healthy.Count < minHealthySamples)
        {
            return new RecoveryEvaluation(
                false,
                false,
                $"Need {minHealthySamples} healthy reported-safe samples; have {healthy.Count}.");
        }

        if (healthy.Count != inWindow.Count)
        {
            return new RecoveryEvaluation(
                false,
                true,
                "Non-healthy or non-safe reported samples appeared during observation; resetting window.");
        }

        if (now - observationStartedAt < TimeSpan.FromSeconds(observationSeconds))
        {
            return new RecoveryEvaluation(
                false,
                false,
                $"Observation window incomplete ({(now - observationStartedAt).TotalSeconds:F1}s / {observationSeconds}s).");
        }

        if (healthy[^1].Timestamp - healthy[0].Timestamp < TimeSpan.FromSeconds(Math.Max(1, observationSeconds - maxSampleGapSeconds)))
        {
            return new RecoveryEvaluation(
                false,
                false,
                "Healthy samples do not yet span the observation window.");
        }

        return new RecoveryEvaluation(true, false, "Continuous healthy reported-safe telemetry verified.");
    }
}
