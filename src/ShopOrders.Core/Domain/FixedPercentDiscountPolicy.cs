namespace ShopOrders.Core.Domain;

/// <summary>
/// Фіксована відсоткова знижка (композиція замість ієрархії знижок).
/// </summary>
public sealed class FixedPercentDiscountPolicy : IDiscountPolicy
{
    private readonly Discount _discount;

    /// <summary>
    /// Створює політику з фіксованою часткою.
    /// </summary>
    /// <param name="rate">Частка знижки.</param>
    public FixedPercentDiscountPolicy(decimal rate)
    {
        this._discount = new Discount(rate);
    }

    /// <inheritdoc />
    public Discount Resolve(Money subtotal)
    {
        _ = subtotal;
        return this._discount;
    }
}
