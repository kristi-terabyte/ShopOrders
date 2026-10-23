using ShopOrders.Core.Domain;

namespace ShopOrders.Tests;

public sealed class OrderDomainTests
{
    [Fact]
    public void AddLine_WhenShipped_Throws()
    {
        Order order = CreateConfirmedOrder();
        order.Ship();

        Assert.Throws<InvalidOperationException>(() =>
            order.AddLine(new OrderLine("Mouse", 1, new Money(10m))));
    }

    [Fact]
    public void Cancel_WhenShipped_Throws()
    {
        Order order = CreateConfirmedOrder();
        order.Ship();

        Assert.Throws<InvalidOperationException>(() => order.Cancel());
    }

    [Fact]
    public void CalculateTotals_SplitsIntoShortMethods_AndRoundsMoney()
    {
        Customer customer = new(1, "Test", "t@example.com");
        Order order = new(1, customer);
        order.AddLine(new OrderLine("Cable", 3, new Money(10.005m)));
        order.ApplyDiscount(new Discount(0.10m));

        OrderTotals totals = order.CalculateTotals();

        Assert.Equal(30.03m, totals.Subtotal.Amount);
        Assert.Equal(3.00m, totals.DiscountAmount.Amount);
        Assert.Equal(27.03m, totals.NetAfterDiscount.Amount);
        Assert.Equal(5.41m, totals.VatAmount.Amount);
        Assert.Equal(32.44m, totals.GrandTotal.Amount);
    }

    [Fact]
    public void Money_RejectsNegativeAmount()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new Money(-1m));
    }

    [Fact]
    public void Customer_RejectsEmailWithoutAt()
    {
        Assert.Throws<ArgumentException>(() => new Customer(1, "A", "bad"));
    }

    private static Order CreateConfirmedOrder()
    {
        Customer customer = new(1, "Test", "t@example.com");
        Order order = new(5, customer);
        order.AddLine(new OrderLine("Item", 1, new Money(100m)));
        order.Confirm();
        return order;
    }
}
