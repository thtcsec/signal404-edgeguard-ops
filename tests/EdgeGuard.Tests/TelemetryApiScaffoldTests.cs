using System.Net;
using System.Net.Http.Json;

namespace EdgeGuard.Tests;

public sealed class TelemetryApiScaffoldTests : IClassFixture<TelemetryApiFactory>
{
    private readonly TelemetryApiFactory _factory;

    public TelemetryApiScaffoldTests(TelemetryApiFactory factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Health_ReportsScaffoldProcess()
    {
        var client = _factory.CreateClient();

        var response = await client.GetAsync("/health");
        var body = await response.Content.ReadFromJsonAsync<HealthBody>();

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.NotNull(body);
        Assert.Equal("healthy", body.Status);
        Assert.Equal("telemetry-api", body.Service);
        Assert.True(body.Scaffold);
    }

    [Fact]
    public async Task Telemetry_ReturnsNotImplemented()
    {
        var client = _factory.CreateClient();

        var response = await client.PostAsync("/telemetry", new StringContent(string.Empty));

        Assert.Equal(HttpStatusCode.NotImplemented, response.StatusCode);
        var body = await response.Content.ReadAsStringAsync();
        Assert.Contains("not implemented", body, StringComparison.OrdinalIgnoreCase);
    }

    private sealed record HealthBody(string Status, string Service, bool Scaffold);
}
