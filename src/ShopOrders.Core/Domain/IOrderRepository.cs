namespace ShopOrders.Core.Domain;

/// <summary>
/// Абстракція сховища замовлень (SOLID: DIP).
/// </summary>
public interface IOrderRepository
{
    /// <summary>
    /// Зберігає або оновлює замовлення.
    /// </summary>
    /// <param name="order">Замовлення.</param>
    void Save(Order order);

    /// <summary>
    /// Шукає замовлення за ідентифікатором.
    /// </summary>
    /// <param name="orderId">Ідентифікатор.</param>
    /// <returns>Замовлення або null.</returns>
    Order? GetById(int orderId);

    /// <summary>
    /// Повертає всі збережені замовлення.
    /// </summary>
    /// <returns>Колекція замовлень.</returns>
    IReadOnlyList<Order> GetAll();
}
