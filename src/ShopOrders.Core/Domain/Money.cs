namespace ShopOrders.Core.Domain;

/// <summary>
/// Незмінна грошова сума у гривні. Інваріант: Amount >= 0; округлення до 2 знаків.
/// Заборонено використовувати double для грошових розрахунків.
/// </summary>
public readonly record struct Money : IComparable<Money>
{
    /// <summary>
    /// Нульова сума.
    /// </summary>
    public static readonly Money Zero = new(0m);

    /// <summary>
    /// Ініціалізує суму з округленням до копійок (AwayFromZero).
    /// </summary>
    /// <param name="amount">Невід'ємна сума.</param>
    /// <exception cref="ArgumentOutOfRangeException">Якщо amount &lt; 0.</exception>
    public Money(decimal amount)
    {
        if (amount < 0m)
        {
            throw new ArgumentOutOfRangeException(nameof(amount), amount, "Money amount must be non-negative.");
        }

        this.Amount = decimal.Round(amount, FinancialConstants.MoneyDecimalPlaces, MidpointRounding.AwayFromZero);
    }

    /// <summary>
    /// Сума у гривнях.
    /// </summary>
    public decimal Amount { get; }

    /// <summary>
    /// Додає дві суми.
    /// </summary>
    public static Money operator +(Money left, Money right) => new(left.Amount + right.Amount);

    /// <summary>
    /// Віднімає суму (результат не може бути від'ємним).
    /// </summary>
    public static Money operator -(Money left, Money right)
    {
        decimal result = left.Amount - right.Amount;
        if (result < 0m)
        {
            throw new InvalidOperationException("Money subtraction would produce a negative amount.");
        }

        return new Money(result);
    }

    /// <summary>
    /// Множить суму на цілу кількість (наприклад, qty * unit price).
    /// </summary>
    public static Money operator *(Money money, int multiplier)
    {
        if (multiplier < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(multiplier), multiplier, "Multiplier must be non-negative.");
        }

        return new Money(money.Amount * multiplier);
    }

    /// <inheritdoc />
    public int CompareTo(Money other) => this.Amount.CompareTo(other.Amount);

    /// <inheritdoc />
    public override string ToString() => $"{this.Amount:F2} UAH";
}
