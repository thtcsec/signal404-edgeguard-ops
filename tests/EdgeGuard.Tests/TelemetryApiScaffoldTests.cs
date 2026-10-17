using System.Net;
using System.Net.Http.Json;
using System.Text;

namespace EdgeGuard.Tests;

public sealed class TelemetryApiScaffoldTests : IClassFixture<TelemetryApiFactory>
{
    private readonly TelemetryApiFactory _factory;

    public TelemetryApiScaffoldTests(TelemetryApiFactory factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Health_ReportsApiProcess()
    {
        var client = _factory.CreateClient();

        var response = await client.GetAsync("/health");
        var body = await response.Content.ReadFromJsonAsync<HealthBody>();

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.NotNull(body);
        Assert.Equal("telemetry-api", body.Service);
        Assert.False(body.Scaffold);
    }

    [Fact]
    public async Task Telemetry_AcceptsValidPayload()
    {
        var client = _factory.CreateClient();
        var payload = new
        {
            deviceId = "edge-test-001",
            site = "factory-a",
            line = "line-03",
            timestamp = DateTimeOffset.UtcNow,
            cpuUsage = 42.0,
            memoryUsage = 55.0,
            cpuTemperature = 62.0,
            gpuTemperature = 70.0,
            gpuUsage = 80.0,
            fps = 28.0,
            inferenceLatencyMs = 40.0,
            packetLossPct = 0.1,
            networkLatencyMs = 10.0,
            droppedFrames = 1,
            profile = "full",
            status = "healthy"
        };

        var response = await client.PostAsJsonAsync("/telemetry", payload);

        Assert.Equal(HttpStatusCode.Accepted, response.StatusCode);
        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("edge-test-001", body, StringComparison.Ordinal);
    }

    [Fact]
    public async Task Telemetry_RejectsMissingDeviceId()
    {
        var client = _factory.CreateClient();
        var json = """
            {
              "deviceId": "",
              "site": "factory-a",
              "line": "line-03",
              "timestamp": "2026-10-17T00:00:00Z",
              "cpuUsage": 1,
              "memoryUsage": 1,
              "cpuTemperature": 1,
              "gpuTemperature": 1,
              "gpuUsage": 1,
              "fps": 1,
              "inferenceLatencyMs": 1,
              "packetLossPct": 0,
              "networkLatencyMs": 1,
              "droppedFrames": 0,
              "profile": "full",
              "status": "healthy"
            }
            """;

        var response = await client.PostAsync(
            "/telemetry",
            new StringContent(json, Encoding.UTF8, "application/json"));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    private sealed record HealthBody(string Status, string Service, bool Scaffold, bool MongoOk);
}
