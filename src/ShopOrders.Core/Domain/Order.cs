namespace ShopOrders.Core.Domain;

/// <summary>
/// Агрегат замовлення інтернет-магазину.
/// Інваріант: Id &gt; 0; зі стану Shipped не можна повернутися до New;
/// рядки змінюються лише у статусі New.
/// </summary>
public sealed class Order
{
    private readonly List<OrderLine> _lines = new();
    private Discount _appliedDiscount = Discount.None;

    /// <summary>
    /// Створює нове замовлення.
    /// </summary>
    /// <param name="id">Ідентифікатор (&gt; 0).</param>
    /// <param name="customer">Клієнт.</param>
    public Order(int id, Customer customer)
    {
        if (id <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(id), id, "Order id must be positive.");
        }

        ArgumentNullException.ThrowIfNull(customer);

        this.Id = id;
        this.Customer = customer;
        this.Status = OrderStatus.New;
        this.CreatedOn = DateOnly.FromDateTime(DateTime.UtcNow);
    }

    /// <summary>
    /// Ідентифікатор замовлення.
    /// </summary>
    public int Id { get; }

    /// <summary>
    /// Клієнт.
    /// </summary>
    public Customer Customer { get; }

    /// <summary>
    /// Поточний статус.
    /// </summary>
    public OrderStatus Status { get; private set; }

    /// <summary>
    /// Дата створення (UTC, календарна).
    /// </summary>
    public DateOnly CreatedOn { get; }

    /// <summary>
    /// Застосована знижка.
    /// </summary>
    public Discount AppliedDiscount => this._appliedDiscount;

    /// <summary>
    /// Рядки замовлення (лише для читання).
    /// </summary>
    public IReadOnlyList<OrderLine> Lines => this._lines.AsReadOnly();

    /// <summary>
    /// Додає рядок (лише у статусі New).
    /// </summary>
    /// <param name="line">Рядок замовлення.</param>
    public void AddLine(OrderLine line)
    {
        ArgumentNullException.ThrowIfNull(line);
        this.EnsureEditable();
        this._lines.Add(line);
    }

    /// <summary>
    /// Застосовує знижку (лише у статусі New).
    /// </summary>
    /// <param name="discount">Знижка.</param>
    public void ApplyDiscount(Discount discount)
    {
        this.EnsureEditable();
        this._appliedDiscount = discount;
    }

    /// <summary>
    /// Підтверджує замовлення (New → Confirmed). Потрібен хоча б один рядок.
    /// </summary>
    public void Confirm()
    {
        if (this.Status != OrderStatus.New)
        {
            throw new InvalidOperationException($"Cannot confirm order in status {this.Status}.");
        }

        if (this._lines.Count == 0)
        {
            throw new InvalidOperationException("Cannot confirm an order without lines.");
        }

        this.Status = OrderStatus.Confirmed;
    }

    /// <summary>
    /// Відправляє замовлення (Confirmed → Shipped).
    /// </summary>
    public void Ship()
    {
        if (this.Status != OrderStatus.Confirmed)
        {
            throw new InvalidOperationException($"Cannot ship order in status {this.Status}.");
        }

        this.Status = OrderStatus.Shipped;
    }

    /// <summary>
    /// Скасовує замовлення (недоступно зі Shipped).
    /// </summary>
    public void Cancel()
    {
        if (this.Status == OrderStatus.Shipped)
        {
            throw new InvalidOperationException("Cannot cancel a shipped order.");
        }

        this.Status = OrderStatus.Cancelled;
    }

    /// <summary>
    /// Обчислює підсумки замовлення (query, без побічних ефектів — CQS).
    /// </summary>
    /// <returns>Підсумки з ПДВ.</returns>
    public OrderTotals CalculateTotals()
    {
        Money subtotal = this.SumLineTotals();
        Money netAfterDiscount = this._appliedDiscount.ApplyTo(subtotal);
        Money discountAmount = subtotal - netAfterDiscount;
        Money vatAmount = this.CalculateVat(netAfterDiscount);
        Money grandTotal = netAfterDiscount + vatAmount;

        return new OrderTotals(subtotal, discountAmount, netAfterDiscount, vatAmount, grandTotal);
    }

    private Money SumLineTotals()
    {
        Money sum = Money.Zero;
        foreach (OrderLine line in this._lines)
        {
            sum += line.LineTotal;
        }

        return sum;
    }

    private Money CalculateVat(Money netAmount)
    {
        decimal vat = netAmount.Amount * FinancialConstants.VatRate;
        return new Money(vat);
    }

    private void EnsureEditable()
    {
        if (this.Status != OrderStatus.New)
        {
            throw new InvalidOperationException($"Order {this.Id} is not editable in status {this.Status}.");
        }
    }
}
