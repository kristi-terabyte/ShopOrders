namespace ShopOrders.Core.Application;

/// <summary>
/// Тип-результат операції без значення (успіх / помилка).
/// </summary>
public class Result
{
    /// <summary>
    /// Initializes a new instance of the <see cref="Result"/> class.
    /// </summary>
    /// <param name="isSuccess">Чи успішно.</param>
    /// <param name="error">Текст помилки.</param>
    protected Result(bool isSuccess, string? error)
    {
        if (isSuccess && error is not null)
        {
            throw new InvalidOperationException("Successful result cannot have an error message.");
        }

        if (!isSuccess && string.IsNullOrWhiteSpace(error))
        {
            throw new InvalidOperationException("Failed result must have an error message.");
        }

        this.IsSuccess = isSuccess;
        this.Error = error;
    }

    /// <summary>
    /// Gets a value indicating whether the operation succeeded.
    /// </summary>
    public bool IsSuccess { get; }

    /// <summary>
    /// Gets a value indicating whether the operation failed.
    /// </summary>
    public bool IsFailure => !this.IsSuccess;

    /// <summary>
    /// Gets the error message (null on success).
    /// </summary>
    public string? Error { get; }

    /// <summary>
    /// Успішний результат.
    /// </summary>
    /// <returns>Result.</returns>
    public static Result Success()
    {
        return new Result(true, null);
    }

    /// <summary>
    /// Невдалий результат.
    /// </summary>
    /// <param name="error">Текст помилки.</param>
    /// <returns>Result.</returns>
    public static Result Failure(string error)
    {
        return new Result(false, error);
    }

    /// <summary>
    /// Успішний результат зі значенням.
    /// </summary>
    /// <typeparam name="T">Тип значення.</typeparam>
    /// <param name="value">Значення.</param>
    /// <returns>Result&lt;T&gt;.</returns>
    public static Result<T> Success<T>(T value)
    {
        return new Result<T>(value);
    }

    /// <summary>
    /// Невдалий результат зі значенням.
    /// </summary>
    /// <typeparam name="T">Тип значення.</typeparam>
    /// <param name="error">Текст помилки.</param>
    /// <returns>Result&lt;T&gt;.</returns>
    public static Result<T> Failure<T>(string error)
    {
        return new Result<T>(error);
    }
}

/// <summary>
/// Тип-результат операції зі значенням.
/// </summary>
/// <typeparam name="T">Тип значення.</typeparam>
public sealed class Result<T> : Result
{
    private readonly T? _value;

    /// <summary>
    /// Initializes a new successful instance of the <see cref="Result{T}"/> class.
    /// </summary>
    /// <param name="value">Значення.</param>
    internal Result(T value)
        : base(true, null)
    {
        this._value = value;
    }

    /// <summary>
    /// Initializes a new failed instance of the <see cref="Result{T}"/> class.
    /// </summary>
    /// <param name="error">Текст помилки.</param>
    internal Result(string error)
        : base(false, error)
    {
        this._value = default;
    }

    /// <summary>
    /// Gets the value when successful.
    /// </summary>
    /// <exception cref="InvalidOperationException">Якщо результат неуспішний.</exception>
    public T Value
    {
        get
        {
            if (this.IsFailure)
            {
                throw new InvalidOperationException("Cannot read Value from a failed result.");
            }

            return this._value!;
        }
    }
}
