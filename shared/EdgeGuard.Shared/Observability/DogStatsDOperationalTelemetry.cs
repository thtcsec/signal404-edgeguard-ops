using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Persistence;
using StatsdClient;

namespace EdgeGuard.Shared.Observability;

public sealed class DogStatsDOperationalTelemetry : IOperationalTelemetry, IDisposable
{
    private readonly DogStatsdService _statsd;
    private readonly string _environmentName;
    private readonly bool _owned;

    public DogStatsDOperationalTelemetry(string agentHost, int dogStatsDPort, string environmentName = "development")
    {
        _environmentName = string.IsNullOrWhiteSpace(environmentName) ? "development" : environmentName;
        _statsd = new DogStatsdService();
        _statsd.Configure(new StatsdConfig
        {
            StatsdServerName = agentHost,
            StatsdPort = dogStatsDPort,
            Prefix = string.Empty
        });
        _owned = true;
    }

    public void RecordDeviceSample(TelemetryReading reading)
    {
        var tags = new[]
        {
            $"env:{_environmentName}",
            $"{MetricTags.DeviceId}:{reading.Metadata.DeviceId}",
            $"{MetricTags.Site}:{reading.Metadata.Site}",
            $"{MetricTags.Line}:{reading.Metadata.Line}",
            $"{MetricTags.Profile}:{DomainMappings.FormatProfile(reading.Profile)}",
            "device_type:edge-camera"
        };

        _statsd.Gauge(MetricNames.CpuUsage, reading.CpuUsage, tags: tags);
        _statsd.Gauge(MetricNames.MemoryUsage, reading.MemoryUsage, tags: tags);
        _statsd.Gauge(MetricNames.CpuTemperature, reading.CpuTemperature, tags: tags);
        _statsd.Gauge(MetricNames.GpuTemperature, reading.GpuTemperature, tags: tags);
        _statsd.Gauge(MetricNames.GpuUsage, reading.GpuUsage, tags: tags);
        _statsd.Gauge(MetricNames.Fps, reading.Fps, tags: tags);
        _statsd.Gauge(MetricNames.InferenceLatency, reading.InferenceLatencyMs, tags: tags);
        _statsd.Gauge(MetricNames.PacketLoss, reading.PacketLossPct, tags: tags);
        _statsd.Gauge(MetricNames.NetworkLatency, reading.NetworkLatencyMs, tags: tags);
        _statsd.Gauge(MetricNames.DroppedFrames, reading.DroppedFrames, tags: tags);
    }

    public void RecordActiveIncidents(int count)
    {
        _statsd.Gauge(MetricNames.IncidentActive, count, tags: [$"env:{_environmentName}"]);
    }

    public void RecordRemediation(RemediationActionType actionType)
    {
        _statsd.Increment(
            MetricNames.RemediationCount,
            tags:
            [
                $"env:{_environmentName}",
                $"action_type:{DomainMappings.FormatRemediationAction(actionType)}"
            ]);
    }

    public void Dispose()
    {
        if (_owned)
        {
            _statsd.Dispose();
        }
    }
}
