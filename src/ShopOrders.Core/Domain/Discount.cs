namespace ShopOrders.Core.Domain;

/// <summary>
/// Незмінна знижка як частка від 0 до MaxDiscountPercent.
/// Інваріант: MinDiscountPercent &lt;= Rate &lt;= MaxDiscountPercent.
/// </summary>
public readonly record struct Discount
{
    /// <summary>
    /// Відсутність знижки.
    /// </summary>
    public static readonly Discount None = new(FinancialConstants.MinDiscountPercent);

    /// <summary>
    /// Створює знижку.
    /// </summary>
    /// <param name="rate">Частка (наприклад 0.10m = 10 %).</param>
    public Discount(decimal rate)
    {
        if (rate < FinancialConstants.MinDiscountPercent || rate > FinancialConstants.MaxDiscountPercent)
        {
            throw new ArgumentOutOfRangeException(
                nameof(rate),
                rate,
                $"Discount rate must be between {FinancialConstants.MinDiscountPercent} and {FinancialConstants.MaxDiscountPercent}.");
        }

        this.Rate = rate;
    }

    /// <summary>
    /// Частка знижки.
    /// </summary>
    public decimal Rate { get; }

    /// <summary>
    /// Застосовує знижку до суми.
    /// </summary>
    /// <param name="subtotal">Базова сума.</param>
    /// <returns>Сума після знижки.</returns>
    public Money ApplyTo(Money subtotal)
    {
        decimal discounted = subtotal.Amount * (1m - this.Rate);
        return new Money(discounted);
    }

    /// <inheritdoc />
    public override string ToString() => $"{this.Rate:P0}";
}
