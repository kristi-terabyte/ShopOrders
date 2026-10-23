using ShopOrders.Core;
using ShopOrders.Core.Application;
using ShopOrders.Core.Domain;
using ShopOrders.Core.Infrastructure;
using ShopOrders.Tests.Fakes;

namespace ShopOrders.Tests;

public sealed class AdditionalCoverageTests
{
    [Fact]
    public void FixedPercentDiscountPolicy_AppliesPercent()
    {
        IDiscountPolicy policy = new FixedPercentDiscountPolicy(0.10m);
        Money subtotal = new(200m);
        Discount d = policy.Resolve(subtotal);
        Assert.Equal(0.10m, d.Rate);
        Assert.Equal(180m, d.ApplyTo(subtotal).Amount);
    }

    [Fact]
    public void Order_Confirm_WithoutLines_Throws()
    {
        Order order = new(1, new Customer(1, "A", "a@b.c"));
        Assert.Throws<InvalidOperationException>(() => order.Confirm());
    }

    [Fact]
    public void Order_Ship_FromNew_Throws()
    {
        Order order = new(1, new Customer(1, "A", "a@b.c"));
        order.AddLine(new OrderLine("X", 1, new Money(10m)));
        Assert.Throws<InvalidOperationException>(() => order.Ship());
    }

    [Fact]
    public void Order_Cancel_FromNew_Ok()
    {
        Order order = new(1, new Customer(1, "A", "a@b.c"));
        order.Cancel();
        Assert.Equal(OrderStatus.Cancelled, order.Status);
    }

    [Fact]
    public void OrderLine_RejectsZeroQuantity()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new OrderLine("X", 0, new Money(1m)));
    }

    [Fact]
    public void Discount_None_DoesNotChangeMoney()
    {
        Money m = new(50m);
        Assert.Equal(50m, Discount.None.ApplyTo(m).Amount);
    }

    [Fact]
    public void InMemoryRepository_Roundtrip()
    {
        InMemoryOrderRepository repo = new();
        Order order = new(9, new Customer(1, "A", "a@b.c"));
        order.AddLine(new OrderLine("P", 2, new Money(5m)));
        repo.Save(order);
        Order? loaded = repo.GetById(9);
        Assert.NotNull(loaded);
        Assert.Single(repo.GetAll());
        Assert.Single(loaded!.Lines);
        Assert.Equal(2, loaded.Lines[0].Quantity);
    }

    [Fact]
    public void VolumeDiscount_BelowThreshold_Zero()
    {
        IDiscountPolicy policy = new VolumeDiscountPolicy();
        Discount d = policy.Resolve(new Money(999.99m));
        Assert.Equal(0m, d.Rate);
    }

    [Theory]
    [InlineData("10", true, 10)]
    [InlineData("x", false, 0)]
    [InlineData("", false, 0)]
    public void InputParsers_Int(string raw, bool ok, int expected)
    {
        Result<int> r = InputParsers.ParseInt(raw, "qty");
        Assert.Equal(ok, r.IsSuccess);
        if (ok)
        {
            Assert.Equal(expected, r.Value);
        }
    }

    [Fact]
    public void VersionInfo_IsNonEmpty()
    {
        Assert.False(string.IsNullOrWhiteSpace(VersionInfo.Version));
    }

    [Fact]
    public void OrderService_Create_WithFakeRepo()
    {
        FakeOrderRepository repo = new();
        OrderService sut = new(repo, new VolumeDiscountPolicy(), new NullLogger<OrderService>());
        Result<int> result = sut.CreateOrder(new CreateOrderRequest(1, "Ann", "ann@ex.com"));
        Assert.True(result.IsSuccess);
        Assert.Equal(1, repo.SaveCallCount);
    }
}
