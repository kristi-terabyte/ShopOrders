namespace ShopOrders.Core.Domain;

/// <summary>
/// Знижка 5 % при сумі рядків від <see cref="FinancialConstants.VolumeDiscountThreshold"/>.
/// </summary>
public sealed class VolumeDiscountPolicy : IDiscountPolicy
{
    /// <inheritdoc />
    public Discount Resolve(Money subtotal)
    {
        if (subtotal.Amount >= FinancialConstants.VolumeDiscountThreshold)
        {
            return new Discount(FinancialConstants.VolumeDiscountRate);
        }

        return Discount.None;
    }
}
