namespace ShopOrders.Core.Domain;

/// <summary>
/// Політика визначення знижки для замовлення (SOLID: OCP / DIP).
/// </summary>
public interface IDiscountPolicy
{
    /// <summary>
    /// Обчислює знижку за сумою рядків (без ПДВ).
    /// </summary>
    /// <param name="subtotal">Сума рядків.</param>
    /// <returns>Знижка.</returns>
    Discount Resolve(Money subtotal);
}
