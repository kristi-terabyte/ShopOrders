using System.Globalization;

namespace ShopOrders.Core.Application;

/// <summary>
/// Безпечний розбір введення користувача (без «німого» int.Parse).
/// </summary>
public static class InputParsers
{
    /// <summary>
    /// Розбирає ціле число.
    /// </summary>
    /// <param name="text">Рядок.</param>
    /// <param name="fieldName">Ім'я поля для повідомлення.</param>
    /// <returns>Result з int.</returns>
    public static Result<int> ParseInt(string? text, string fieldName)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(fieldName);

        if (string.IsNullOrWhiteSpace(text))
        {
            return Result.Failure<int>($"{fieldName} is required.");
        }

        if (!int.TryParse(text.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int value))
        {
            return Result.Failure<int>($"{fieldName} must be an integer.");
        }

        return Result.Success(value);
    }

    /// <summary>
    /// Розбирає decimal (гроші / відсотки).
    /// </summary>
    /// <param name="text">Рядок.</param>
    /// <param name="fieldName">Ім'я поля.</param>
    /// <returns>Result з decimal.</returns>
    public static Result<decimal> ParseDecimal(string? text, string fieldName)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(fieldName);

        if (string.IsNullOrWhiteSpace(text))
        {
            return Result.Failure<decimal>($"{fieldName} is required.");
        }

        if (!decimal.TryParse(text.Trim(), NumberStyles.Number, CultureInfo.InvariantCulture, out decimal value))
        {
            return Result.Failure<decimal>($"{fieldName} must be a decimal number (InvariantCulture).");
        }

        return Result.Success(value);
    }
}
