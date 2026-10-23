namespace ShopOrders.Core.Domain;

/// <summary>
/// Результат розрахунку підсумків замовлення (CQS: query result).
/// </summary>
/// <param name="Subtotal">Сума рядків без знижки та ПДВ.</param>
/// <param name="DiscountAmount">Сума знижки.</param>
/// <param name="NetAfterDiscount">Сума після знижки, без ПДВ.</param>
/// <param name="VatAmount">Сума ПДВ.</param>
/// <param name="GrandTotal">Підсумок з ПДВ.</param>
public sealed record OrderTotals(
    Money Subtotal,
    Money DiscountAmount,
    Money NetAfterDiscount,
    Money VatAmount,
    Money GrandTotal);
