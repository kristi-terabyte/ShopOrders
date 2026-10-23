using ShopOrders.Core.Application;

namespace ShopOrders.Tests;

public sealed class InputParsersTests
{
    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("  ")]
    [InlineData("abc")]
    public void ParseInt_Invalid_ReturnsFailure(string? text)
    {
        Result<int> result = InputParsers.ParseInt(text, "Qty");

        Assert.True(result.IsFailure);
    }

    [Fact]
    public void ParseInt_Valid_ReturnsValue()
    {
        Result<int> result = InputParsers.ParseInt("42", "Qty");

        Assert.True(result.IsSuccess);
        Assert.Equal(42, result.Value);
    }

    [Fact]
    public void ParseDecimal_UsesInvariantCulture()
    {
        Result<decimal> result = InputParsers.ParseDecimal("19.99", "Price");

        Assert.True(result.IsSuccess);
        Assert.Equal(19.99m, result.Value);
    }
}
