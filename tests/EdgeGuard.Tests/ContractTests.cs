using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;

namespace EdgeGuard.Tests;

public sealed class ContractTests
{
    [Fact]
    public void MetricNames_MatchPlannedDatadogContract()
    {
        Assert.Equal("edgeguard.device.cpu_usage", MetricNames.CpuUsage);
        Assert.Equal("edgeguard.device.memory_usage", MetricNames.MemoryUsage);
        Assert.Equal("edgeguard.device.cpu_temperature", MetricNames.CpuTemperature);
        Assert.Equal("edgeguard.device.gpu_temperature", MetricNames.GpuTemperature);
        Assert.Equal("edgeguard.device.gpu_usage", MetricNames.GpuUsage);
        Assert.Equal("edgeguard.device.fps", MetricNames.Fps);
        Assert.Equal("edgeguard.device.inference_latency", MetricNames.InferenceLatency);
        Assert.Equal("edgeguard.device.packet_loss", MetricNames.PacketLoss);
        Assert.Equal("edgeguard.device.network_latency", MetricNames.NetworkLatency);
        Assert.Equal("edgeguard.device.dropped_frames", MetricNames.DroppedFrames);
        Assert.Equal("edgeguard.incident.active", MetricNames.IncidentActive);
        Assert.Equal("edgeguard.remediation.count", MetricNames.RemediationCount);
    }

    [Fact]
    public void IncidentLifecycle_IncludesRecoveryStates()
    {
        Assert.Equal(
            [
                IncidentStatus.Open,
                IncidentStatus.Investigating,
                IncidentStatus.Mitigating,
                IncidentStatus.Recovering,
                IncidentStatus.Resolved
            ],
            Enum.GetValues<IncidentStatus>());
    }
}
