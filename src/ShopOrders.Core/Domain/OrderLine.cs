namespace ShopOrders.Core.Domain;

/// <summary>
/// Незмінний рядок замовлення.
/// Інваріант: Quantity &gt; 0; UnitPrice &gt;= 0; ProductName не порожній.
/// </summary>
public sealed class OrderLine
{
    /// <summary>
    /// Створює рядок замовлення.
    /// </summary>
    /// <param name="productName">Назва товару.</param>
    /// <param name="quantity">Кількість (&gt; 0).</param>
    /// <param name="unitPrice">Ціна за одиницю.</param>
    public OrderLine(string productName, int quantity, Money unitPrice)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(productName);

        if (quantity <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(quantity), quantity, "Quantity must be greater than zero.");
        }

        this.ProductName = productName.Trim();
        this.Quantity = quantity;
        this.UnitPrice = unitPrice;
    }

    /// <summary>
    /// Назва товару.
    /// </summary>
    public string ProductName { get; }

    /// <summary>
    /// Кількість одиниць.
    /// </summary>
    public int Quantity { get; }

    /// <summary>
    /// Ціна за одиницю.
    /// </summary>
    public Money UnitPrice { get; }

    /// <summary>
    /// Вартість рядка (quantity × unit price) без знижки та ПДВ.
    /// </summary>
    public Money LineTotal => this.UnitPrice * this.Quantity;
}
