using Microsoft.Extensions.Logging;

namespace ShopOrders.Tests.Fakes;

/// <summary>
/// Мінімальний логер-заглушка для тестів (без побічних ефектів).
/// </summary>
public sealed class NullLogger<T> : ILogger<T>
{
    public IDisposable? BeginScope<TState>(TState state)
        where TState : notnull
        => NullScope.Instance;

    public bool IsEnabled(LogLevel logLevel) => false;

    public void Log<TState>(
        LogLevel logLevel,
        EventId eventId,
        TState state,
        Exception? exception,
        Func<TState, Exception?, string> formatter)
    {
    }

    private sealed class NullScope : IDisposable
    {
        public static readonly NullScope Instance = new();

        public void Dispose()
        {
        }
    }
}
