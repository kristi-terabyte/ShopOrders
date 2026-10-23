using ShopOrders.Core.Application;
using ShopOrders.Core.Domain;
using ShopOrders.Tests.Fakes;

namespace ShopOrders.Tests;

public sealed class OrderServiceTests
{
    private readonly FakeOrderRepository _repository = new();
    private readonly VolumeDiscountPolicy _policy = new();
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        this._sut = new OrderService(this._repository, this._policy, new NullLogger<OrderService>());
    }

    [Fact]
    public void CreateOrder_WithValidCustomer_ReturnsSuccessAndPersists()
    {
        Result<int> result = this._sut.CreateOrder(
            new CreateOrderRequest(10, "Ivan Petrenko", "ivan@example.com"));

        Assert.True(result.IsSuccess);
        Assert.Equal(1, result.Value);
        Assert.NotNull(this._repository.GetById(1));
        Assert.True(this._repository.SaveCallCount >= 1);
    }

    [Fact]
    public void CreateOrder_WithInvalidEmail_ReturnsFailure()
    {
        Result<int> result = this._sut.CreateOrder(
            new CreateOrderRequest(10, "Ivan", "no-at-sign"));

        Assert.True(result.IsFailure);
        Assert.Contains("@", result.Error!, StringComparison.Ordinal);
    }

    [Fact]
    public void AddLine_ThenGetTotals_ComputesVatWithDecimal()
    {
        int orderId = this._sut.CreateOrder(
            new CreateOrderRequest(1, "Olga", "olga@shop.ua")).Value;

        Result add = this._sut.AddLine(new AddOrderLineRequest(orderId, "Keyboard", 2, 250.00m));
        Assert.True(add.IsSuccess);

        Result<OrderTotals> totals = this._sut.GetTotals(orderId);

        Assert.True(totals.IsSuccess);
        Assert.Equal(500.00m, totals.Value.Subtotal.Amount);
        Assert.Equal(100.00m, totals.Value.VatAmount.Amount);
        Assert.Equal(600.00m, totals.Value.GrandTotal.Amount);
    }

    [Fact]
    public void ApplyPolicyDiscount_WhenVolumeReached_AppliesFivePercent()
    {
        int orderId = this._sut.CreateOrder(
            new CreateOrderRequest(1, "Olga", "olga@shop.ua")).Value;
        this._sut.AddLine(new AddOrderLineRequest(orderId, "Monitor", 2, 600.00m));

        Result<decimal> discount = this._sut.ApplyPolicyDiscount(new ApplyDiscountRequest(orderId));
        Result<OrderTotals> totals = this._sut.GetTotals(orderId);

        Assert.True(discount.IsSuccess);
        Assert.Equal(0.05m, discount.Value);
        Assert.Equal(1200.00m, totals.Value.Subtotal.Amount);
        Assert.Equal(60.00m, totals.Value.DiscountAmount.Amount);
        Assert.Equal(1140.00m, totals.Value.NetAfterDiscount.Amount);
        Assert.Equal(228.00m, totals.Value.VatAmount.Amount);
        Assert.Equal(1368.00m, totals.Value.GrandTotal.Amount);
    }

    [Fact]
    public void GetTotals_WhenOrderMissing_ReturnsFailure()
    {
        Result<OrderTotals> result = this._sut.GetTotals(999);

        Assert.True(result.IsFailure);
        Assert.Contains("999", result.Error!, StringComparison.Ordinal);
    }
}
