namespace ShopOrders.Core.Application;

/// <summary>
/// Запит на створення замовлення.
/// </summary>
/// <param name="CustomerId">Ідентифікатор клієнта.</param>
/// <param name="CustomerName">Ім'я клієнта.</param>
/// <param name="CustomerEmail">Email клієнта.</param>
public sealed record CreateOrderRequest(int CustomerId, string CustomerName, string CustomerEmail);

/// <summary>
/// Запит на додавання рядка.
/// </summary>
/// <param name="OrderId">Ідентифікатор замовлення.</param>
/// <param name="ProductName">Назва товару.</param>
/// <param name="Quantity">Кількість.</param>
/// <param name="UnitPrice">Ціна за одиницю.</param>
public sealed record AddOrderLineRequest(int OrderId, string ProductName, int Quantity, decimal UnitPrice);

/// <summary>
/// Запит на застосування знижки за політикою.
/// </summary>
/// <param name="OrderId">Ідентифікатор замовлення.</param>
public sealed record ApplyDiscountRequest(int OrderId);
