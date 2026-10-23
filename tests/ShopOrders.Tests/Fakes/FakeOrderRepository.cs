using ShopOrders.Core.Domain;

namespace ShopOrders.Tests.Fakes;

/// <summary>
/// Тестовий дубль сховища (in-memory fake).
/// </summary>
public sealed class FakeOrderRepository : IOrderRepository
{
    private readonly Dictionary<int, Order> _store = new();

    public int SaveCallCount { get; private set; }

    public void Save(Order order)
    {
        ArgumentNullException.ThrowIfNull(order);
        this._store[order.Id] = order;
        this.SaveCallCount++;
    }

    public Order? GetById(int orderId)
    {
        return this._store.TryGetValue(orderId, out Order? order) ? order : null;
    }

    public IReadOnlyList<Order> GetAll()
    {
        return this._store.Values.ToList();
    }
}
