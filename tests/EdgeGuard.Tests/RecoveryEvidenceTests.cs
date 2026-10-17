using EdgeGuard.Shared.Domain;

namespace EdgeGuard.Tests;

public sealed class RecoveryEvidenceTests
{
    [Fact]
    public void ContinuousHealthyReportedSafe_Recovers()
    {
        var start = DateTimeOffset.Parse("2026-10-17T10:00:00Z");
        var samples = Enumerable.Range(0, 25)
            .Select(i => Sample(start.AddSeconds(i), DeviceProfile.Safe, DeviceStatus.Healthy, 60, 40, 24))
            .ToList();

        var result = RecoveryEvidence.Evaluate(
            samples,
            DeviceProfile.Safe,
            start,
            start.AddSeconds(24),
            observationSeconds: 20,
            maxStalenessSeconds: 5,
            maxSampleGapSeconds: 5,
            minHealthySamples: 3,
            recoveredGpuMaxC: 75,
            recoveredLatencyMaxMs: 80,
            recoveredFpsMin: 18);

        Assert.True(result.IsRecovered);
        Assert.False(result.ShouldResetObservation);
    }

    [Fact]
    public void StaleTelemetry_ResetsObservation()
    {
        var start = DateTimeOffset.Parse("2026-10-17T10:00:00Z");
        var samples = new List<TelemetryReading>
        {
            Sample(start.AddSeconds(1), DeviceProfile.Safe, DeviceStatus.Healthy, 60, 40, 24)
        };

        var result = RecoveryEvidence.Evaluate(
            samples,
            DeviceProfile.Safe,
            start,
            start.AddSeconds(30),
            observationSeconds: 20,
            maxStalenessSeconds: 5,
            maxSampleGapSeconds: 5,
            minHealthySamples: 3,
            recoveredGpuMaxC: 75,
            recoveredLatencyMaxMs: 80,
            recoveredFpsMin: 18);

        Assert.False(result.IsRecovered);
        Assert.True(result.ShouldResetObservation);
        Assert.Contains("stale", result.Reason, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ReportedFull_IsNotEvidenceOfSafe()
    {
        var start = DateTimeOffset.Parse("2026-10-17T10:00:00Z");
        var samples = Enumerable.Range(0, 25)
            .Select(i => Sample(start.AddSeconds(i), DeviceProfile.Full, DeviceStatus.Healthy, 60, 40, 24))
            .ToList();

        var result = RecoveryEvidence.Evaluate(
            samples,
            DeviceProfile.Safe, // commanded safe, but reported still full
            start,
            start.AddSeconds(24),
            observationSeconds: 20,
            maxStalenessSeconds: 5,
            maxSampleGapSeconds: 5,
            minHealthySamples: 3,
            recoveredGpuMaxC: 75,
            recoveredLatencyMaxMs: 80,
            recoveredFpsMin: 18);

        Assert.False(result.IsRecovered);
    }

    private static TelemetryReading Sample(
        DateTimeOffset ts,
        DeviceProfile profile,
        DeviceStatus status,
        double gpu,
        double latency,
        double fps) =>
        new(
            ts,
            new TelemetryMetadata("edge-001", "factory-a", "line-01"),
            40,
            50,
            55,
            gpu,
            50,
            fps,
            latency,
            0.1,
            10,
            0,
            profile,
            status);
}
