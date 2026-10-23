namespace ShopOrders.Core.Domain;

/// <summary>
/// Статус життєвого циклу замовлення.
/// </summary>
public enum OrderStatus
{
    /// <summary>
    /// Нове замовлення, можна редагувати рядки.
    /// </summary>
    New = 0,

    /// <summary>
    /// Підтверджене, рядки зафіксовані.
    /// </summary>
    Confirmed = 1,

    /// <summary>
    /// Відправлене клієнту.
    /// </summary>
    Shipped = 2,

    /// <summary>
    /// Скасоване.
    /// </summary>
    Cancelled = 3,
}
