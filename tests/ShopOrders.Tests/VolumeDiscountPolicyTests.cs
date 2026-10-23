using ShopOrders.Core.Domain;

namespace ShopOrders.Tests;

public sealed class VolumeDiscountPolicyTests
{
    private readonly VolumeDiscountPolicy _sut = new();

    [Fact]
    public void Resolve_WhenBelowThreshold_ReturnsNone()
    {
        Money subtotal = new(FinancialConstants.VolumeDiscountThreshold - 0.01m);

        Discount discount = this._sut.Resolve(subtotal);

        Assert.Equal(Discount.None, discount);
        Assert.Equal(0m, discount.Rate);
    }

    [Fact]
    public void Resolve_WhenAtThreshold_ReturnsVolumeRate()
    {
        Money subtotal = new(FinancialConstants.VolumeDiscountThreshold);

        Discount discount = this._sut.Resolve(subtotal);

        Assert.Equal(FinancialConstants.VolumeDiscountRate, discount.Rate);
    }

    [Fact]
    public void Resolve_WhenAboveThreshold_ReturnsVolumeRate()
    {
        Money subtotal = new(5000m);

        Discount discount = this._sut.Resolve(subtotal);

        Assert.Equal(FinancialConstants.VolumeDiscountRate, discount.Rate);
    }
}
