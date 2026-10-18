using System.Collections.Concurrent;
using System.Globalization;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace EdgeGuard.Shared.Observability;

/// <summary>
/// Writes one JSON log line per event to a service log file for Datadog Agent file-tail collection.
/// Only serializes primitive structured log values — never reflection metadata from FormattedLogValues.
/// </summary>
public sealed class JsonFileLoggerProvider : ILoggerProvider
{
    private readonly string _filePath;
    private readonly ConcurrentDictionary<string, JsonFileLogger> _loggers = new(StringComparer.Ordinal);
    private readonly object _writeLock = new();

    public JsonFileLoggerProvider(string filePath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(filePath);
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(filePath))!);
        _filePath = Path.GetFullPath(filePath);
    }

    public ILogger CreateLogger(string categoryName) =>
        _loggers.GetOrAdd(categoryName, name => new JsonFileLogger(name, WriteLine));

    public void Dispose() => _loggers.Clear();

    private void WriteLine(string line)
    {
        lock (_writeLock)
        {
            File.AppendAllText(_filePath, line + Environment.NewLine, Encoding.UTF8);
        }
    }

    private sealed class JsonFileLogger(string categoryName, Action<string> write) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

        public bool IsEnabled(LogLevel logLevel) => logLevel != LogLevel.None;

        public void Log<TState>(
            LogLevel logLevel,
            EventId eventId,
            TState state,
            Exception? exception,
            Func<TState, Exception?, string> formatter)
        {
            if (!IsEnabled(logLevel))
            {
                return;
            }

            try
            {
                var payload = new Dictionary<string, object?>(StringComparer.Ordinal)
                {
                    ["timestamp"] = DateTimeOffset.UtcNow.ToString("O"),
                    ["level"] = logLevel.ToString(),
                    ["category"] = categoryName,
                    ["message"] = formatter(state, exception),
                    ["eventId"] = eventId.Id
                };

                if (exception is not null)
                {
                    payload["exception"] = exception.ToString();
                }

                if (state is IEnumerable<KeyValuePair<string, object?>> values)
                {
                    foreach (var pair in values)
                    {
                        if (string.IsNullOrEmpty(pair.Key) || pair.Key is "{OriginalFormat}")
                        {
                            continue;
                        }

                        var safe = ToSafeValue(pair.Value);
                        if (safe is not null)
                        {
                            payload[pair.Key] = safe;
                        }
                    }
                }

                write(JsonSerializer.Serialize(payload));
            }
            catch
            {
                // Never fail the request path because of file logging.
            }
        }

        private static object? ToSafeValue(object? value) =>
            value switch
            {
                null => null,
                string s => s,
                bool or byte or sbyte or short or ushort or int or uint or long or ulong or float or double or decimal => value,
                DateTime dt => dt.ToString("O", CultureInfo.InvariantCulture),
                DateTimeOffset dto => dto.ToString("O", CultureInfo.InvariantCulture),
                Enum e => e.ToString(),
                Guid g => g.ToString(),
                _ => value.ToString()
            };
    }
}
