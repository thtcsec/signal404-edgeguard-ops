using EdgeGuard.ResponseWorker;
using EdgeGuard.Shared.Configuration;
using EdgeGuard.Shared.Contracts;
using EdgeGuard.Shared.Domain;
using EdgeGuard.Shared.Observability;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;

namespace EdgeGuard.Tests;

public sealed class RemediationRetryTests
{
    [Fact]
    public async Task PartialFailure_RetryReusesAction_AndCommandAloneDoesNotResolve()
    {
        var store = new Store { FailIncidentWrite = true };
        await Assert.ThrowsAsync<IOException>(() => Executor(store).ProcessAsync(default));
        Assert.Single(store.Actions);
        Assert.Equal(IncidentStatus.Open, store.Incident.Status);
        // New executor simulates restarting after the action was applied but not linked.
        await Executor(store).ProcessAsync(default);
        Assert.Single(store.Actions);
        Assert.Equal(IncidentStatus.Mitigating, store.Incident.Status);
        await Executor(store).ProcessAsync(default);
        Assert.Equal(IncidentStatus.Mitigating, store.Incident.Status); // no reported-safe samples
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task MissingOrFailedActionVerification_DoesNotResolve(bool failWrite)
    {
        var store = new Store();
        var executor = Executor(store);
        await executor.ProcessAsync(default);
        store.Readings = [Reading(DateTimeOffset.UtcNow)];
        await executor.ProcessAsync(default);
        Assert.Equal(IncidentStatus.Recovering, store.Incident.Status);
        store.Readings.Add(Reading(DateTimeOffset.UtcNow));
        await Task.Delay(1100);
        store.Readings.Add(Reading(DateTimeOffset.UtcNow));
        if (failWrite)
        {
            store.FailActionWrite = true;
            await Assert.ThrowsAsync<IOException>(() => executor.ProcessAsync(default));
        }
        else
        {
            store.Actions.Clear();
            await executor.ProcessAsync(default);
        }
        Assert.Equal(IncidentStatus.Recovering, store.Incident.Status);
    }

    [Fact]
    public async Task HealthyEvidence_VerifiesActionBeforeResolvingIncident()
    {
        var store = new Store();
        var executor = Executor(store);
        await executor.ProcessAsync(default);
        store.Readings = [Reading(DateTimeOffset.UtcNow)];
        await executor.ProcessAsync(default);
        store.Readings.Add(Reading(DateTimeOffset.UtcNow));
        store.Readings.Add(Reading(DateTimeOffset.UtcNow));
        await Task.Delay(1100);
        store.Readings.Add(Reading(DateTimeOffset.UtcNow));
        await executor.ProcessAsync(default);
        Assert.Equal(IncidentStatus.Resolved, store.Incident.Status);
        Assert.Equal(RemediationState.Verified, Assert.Single(store.Actions.Values).State);
        Assert.True(store.ActionVerifiedAtResolve);
    }

    private static SafeProfileRemediationExecutor Executor(Store store) => new(
        store, store, store, store, new NoOpOperationalTelemetry(),
        Options.Create(new RemediationSettings { ObservationSeconds = 1, MinHealthySamples = 2 }),
        NullLogger<SafeProfileRemediationExecutor>.Instance);

    private static TelemetryReading Reading(DateTimeOffset timestamp) => new(timestamp,
        new TelemetryMetadata("edge-001", "fixture", "fixture"), 40, 50, 55, 60, 50, 18, 60,
        0.1, 10, 0, DeviceProfile.Safe, DeviceStatus.Healthy);

    private sealed class Store : IIncidentRepository, IDeviceRepository, ITelemetryRepository, IRemediationActionRepository
    {
        public IncidentRecord Incident = new("fixture", "edge-001", IncidentType.ThermalThrottling,
            IncidentSeverity.High, IncidentStatus.Open, DateTimeOffset.UtcNow, null,
            new IncidentEvidence(95, 180, 12, 0), "thermal", null);
        public DeviceRecord Device = new("edge-001", "fixture", "fixture", "fixture", "synthetic",
            new HardwareInfo("synthetic", "synthetic"), DeviceProfile.Full, DeviceStatus.Degraded, DateTimeOffset.UtcNow);
        public Dictionary<string, RemediationActionRecord> Actions = new();
        public List<TelemetryReading> Readings = new();
        public bool FailIncidentWrite, FailActionWrite, ActionVerifiedAtResolve;
        public Task InsertAsync(IncidentRecord value, CancellationToken ct) { Incident = value; return Task.CompletedTask; }
        Task<IncidentRecord?> IIncidentRepository.GetAsync(string id, CancellationToken ct) => Task.FromResult<IncidentRecord?>(Incident);
        public Task<IncidentRecord?> FindActiveByDeviceAndTypeAsync(string id, IncidentType type, CancellationToken ct) => Task.FromResult<IncidentRecord?>(Incident);
        public Task<IReadOnlyList<IncidentRecord>> ListByStatusesAsync(IReadOnlyCollection<IncidentStatus> statuses, CancellationToken ct) =>
            Task.FromResult<IReadOnlyList<IncidentRecord>>(statuses.Contains(Incident.Status) ? [Incident] : []);
        public Task<int> CountActiveAsync(CancellationToken ct) => Task.FromResult(Incident.Status == IncidentStatus.Resolved ? 0 : 1);
        public Task UpdateAsync(IncidentRecord value, CancellationToken ct)
        {
            if (FailIncidentWrite) { FailIncidentWrite = false; throw new IOException("fixture incident write failure"); }
            if (value.Status == IncidentStatus.Resolved) ActionVerifiedAtResolve = Actions[value.RemediationId!].State == RemediationState.Verified;
            Incident = value; return Task.CompletedTask;
        }
        public Task UpdateStatusAsync(string id, IncidentStatus status, CancellationToken ct) { Incident = Incident with { Status = status }; return Task.CompletedTask; }
        Task<DeviceRecord?> IDeviceRepository.GetAsync(string id, CancellationToken ct) => Task.FromResult<DeviceRecord?>(Device);
        public Task UpsertAsync(DeviceRecord value, CancellationToken ct) { Device = value; return Task.CompletedTask; }
        public Task SetCommandedProfileAsync(string id, DeviceProfile profile, CancellationToken ct) { Device = Device with { Profile = profile }; return Task.CompletedTask; }
        public Task SetStatusAsync(string id, DeviceStatus status, CancellationToken ct) { Device = Device with { Status = status }; return Task.CompletedTask; }
        public Task InsertAsync(TelemetryReading value, CancellationToken ct) { Readings.Add(value); return Task.CompletedTask; }
        public Task<IReadOnlyList<TelemetryReading>> GetRecentAsync(string id, TimeSpan lookback, CancellationToken ct) => Task.FromResult<IReadOnlyList<TelemetryReading>>(Readings);
        public Task InsertAsync(RemediationActionRecord value, CancellationToken ct) { Actions.TryAdd(value.Id, value); return Task.CompletedTask; }
        Task<RemediationActionRecord?> IRemediationActionRepository.GetAsync(string id, CancellationToken ct) => Task.FromResult(Actions.GetValueOrDefault(id));
        public Task UpdateAsync(RemediationActionRecord value, CancellationToken ct)
        {
            if (FailActionWrite) throw new IOException("fixture action write failure");
            Actions[value.Id] = value; return Task.CompletedTask;
        }
    }
}
