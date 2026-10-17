namespace EdgeGuard.Shared.Configuration;

public sealed class AnalyzerSettings
{
    public const string SectionName = "Analyzer";

    public int IntervalSeconds { get; set; } = 10;

    public int LookbackMinutes { get; set; } = 10;

    public double GpuTemperatureThresholdC { get; set; } = 85.0;

    public double GpuTemperatureRiseC { get; set; } = 8.0;

    public double InferenceLatencyThresholdMs { get; set; } = 100.0;

    public double InferenceLatencyRiseMs { get; set; } = 40.0;

    public double FpsFloor { get; set; } = 16.0;

    public double PacketLossMaxPct { get; set; } = 2.0;
}
