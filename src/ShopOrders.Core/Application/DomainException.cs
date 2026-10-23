namespace ShopOrders.Core.Application;

/// <summary>
/// Базовий виняток доменної / прикладної логіки ShopOrders.
/// </summary>
public class DomainException : Exception
{
    /// <summary>
    /// Створює виняток із повідомленням.
    /// </summary>
    /// <param name="message">Текст.</param>
    public DomainException(string message)
        : base(message)
    {
    }

    /// <summary>
    /// Створює виняток із внутрішньою причиною.
    /// </summary>
    /// <param name="message">Текст.</param>
    /// <param name="innerException">Внутрішній виняток.</param>
    public DomainException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}

/// <summary>
/// Порушення правила валідації вхідних даних (барикада).
/// </summary>
public sealed class ValidationException : DomainException
{
    /// <summary>
    /// Створює виняток валідації.
    /// </summary>
    /// <param name="message">Текст.</param>
    public ValidationException(string message)
        : base(message)
    {
    }
}

/// <summary>
/// Замовлення не знайдено у сховищі.
/// </summary>
public sealed class OrderNotFoundException : DomainException
{
    /// <summary>
    /// Створює виняток «не знайдено».
    /// </summary>
    /// <param name="orderId">Ідентифікатор.</param>
    public OrderNotFoundException(int orderId)
        : base($"Order with id {orderId} was not found.")
    {
        this.OrderId = orderId;
    }

    /// <summary>
    /// Ідентифікатор шуканого замовлення.
    /// </summary>
    public int OrderId { get; }
}
