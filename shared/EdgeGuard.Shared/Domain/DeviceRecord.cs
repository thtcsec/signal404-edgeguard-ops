namespace EdgeGuard.Shared.Domain;

public sealed record HardwareInfo(string Cpu, string Gpu);

public sealed record DeviceRecord(
    string Id,
    string Name,
    string Site,
    string Line,
    string DeviceType,
    HardwareInfo Hardware,
    DeviceProfile Profile,
    DeviceStatus Status,
    DateTimeOffset CreatedAt);
