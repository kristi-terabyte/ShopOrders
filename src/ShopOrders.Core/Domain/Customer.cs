namespace ShopOrders.Core.Domain;

/// <summary>
/// Клієнт інтернет-магазину.
/// Інваріант: Id > 0; Email містить '@'; FullName не порожній.
/// </summary>
public sealed class Customer
{
    /// <summary>
    /// Створює клієнта з перевіркою інваріантів.
    /// </summary>
    /// <param name="id">Ідентифікатор (&gt; 0).</param>
    /// <param name="fullName">Повне ім'я.</param>
    /// <param name="email">Електронна адреса.</param>
    public Customer(int id, string fullName, string email)
    {
        if (id <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(id), id, "Customer id must be positive.");
        }

        ArgumentException.ThrowIfNullOrWhiteSpace(fullName);
        ArgumentException.ThrowIfNullOrWhiteSpace(email);

        if (!email.Contains('@', StringComparison.Ordinal))
        {
            throw new ArgumentException("Customer email must contain '@'.", nameof(email));
        }

        this.Id = id;
        this.FullName = fullName.Trim();
        this.Email = email.Trim();
    }

    /// <summary>
    /// Ідентифікатор клієнта.
    /// </summary>
    public int Id { get; }

    /// <summary>
    /// Повне ім'я.
    /// </summary>
    public string FullName { get; }

    /// <summary>
    /// Електронна адреса.
    /// </summary>
    public string Email { get; }
}
