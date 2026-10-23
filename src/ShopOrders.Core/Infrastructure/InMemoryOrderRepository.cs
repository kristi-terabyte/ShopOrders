using ShopOrders.Core.Domain;

namespace ShopOrders.Core.Infrastructure;

/// <summary>
/// In-memory реалізація <see cref="IOrderRepository"/> для консольного демо.
/// </summary>
public sealed class InMemoryOrderRepository : IOrderRepository
{
    private readonly Dictionary<int, Order> _orders = new();

    /// <inheritdoc />
    public void Save(Order order)
    {
        ArgumentNullException.ThrowIfNull(order);
        this._orders[order.Id] = order;
    }

    /// <inheritdoc />
    public Order? GetById(int orderId)
    {
        return this._orders.TryGetValue(orderId, out Order? order) ? order : null;
    }

    /// <inheritdoc />
    public IReadOnlyList<Order> GetAll()
    {
        return this._orders.Values.OrderBy(o => o.Id).ToList();
    }
}
