namespace ShopOrders.Core.Domain;

/// <summary>
/// Іменовані сталі для грошових і податкових розрахунків ShopOrders.
/// </summary>
public static class FinancialConstants
{
    /// <summary>
    /// Ставка ПДВ (20 %). Використовувати лише decimal.
    /// </summary>
    public const decimal VatRate = 0.20m;

    /// <summary>
    /// Кількість знаків після коми для грошових сум.
    /// </summary>
    public const int MoneyDecimalPlaces = 2;

    /// <summary>
    /// Максимальний відсоток знижки (50 %).
    /// </summary>
    public const decimal MaxDiscountPercent = 0.50m;

    /// <summary>
    /// Мінімальний відсоток знижки.
    /// </summary>
    public const decimal MinDiscountPercent = 0.00m;

    /// <summary>
    /// Поріг суми замовлення (без ПДВ) для автоматичної знижки 5 %.
    /// </summary>
    public const decimal VolumeDiscountThreshold = 1000.00m;

    /// <summary>
    /// Автоматична знижка при перевищенні порогу обсягу.
    /// </summary>
    public const decimal VolumeDiscountRate = 0.05m;
}
