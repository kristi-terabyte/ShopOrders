using System.Globalization;
using Microsoft.Extensions.Logging;
using ShopOrders.Core;
using ShopOrders.Core.Application;
using ShopOrders.Core.Domain;

namespace ShopOrders.App;

/// <summary>
/// Консольний інтерфейс ShopOrders (SR3): створення, рядки, знижка, підсумок.
/// </summary>
public sealed class ConsoleUi
{
    private readonly OrderService _orderService;
    private readonly ILogger<ConsoleUi> _logger;
    private int? _currentOrderId;

    /// <summary>
    /// Створює UI.
    /// </summary>
    /// <param name="orderService">Сервіс замовлень.</param>
    /// <param name="logger">Логер.</param>
    public ConsoleUi(OrderService orderService, ILogger<ConsoleUi> logger)
    {
        ArgumentNullException.ThrowIfNull(orderService);
        ArgumentNullException.ThrowIfNull(logger);
        this._orderService = orderService;
        this._logger = logger;
    }

    /// <summary>
    /// Головний цикл меню.
    /// </summary>
    public void Run()
    {
        Console.WriteLine(VersionInfo.GetDisplayString());
        Console.WriteLine("ShopOrders — облік замовлень інтернет-магазину (варіант №1)");
        Console.WriteLine("Автор: Виконавець: студент групи (варіант 1)");
        Console.WriteLine();

        bool running = true;
        while (running)
        {
            this.PrintMenu();
            string? choice = Console.ReadLine();
            switch (choice?.Trim())
            {
                case "1":
                    this.CreateOrder();
                    break;
                case "2":
                    this.AddLine();
                    break;
                case "3":
                    this.ApplyDiscount();
                    break;
                case "4":
                    this.PrintTotals();
                    break;
                case "5":
                    this.ShowOrder();
                    break;
                case "0":
                    running = false;
                    break;
                default:
                    Console.WriteLine("Невідома команда.");
                    break;
            }
        }

        this._logger.LogInformation("Console UI stopped");
    }

    private void PrintMenu()
    {
        string current = this._currentOrderId?.ToString(CultureInfo.InvariantCulture) ?? "немає";
        Console.WriteLine();
        Console.WriteLine($"Поточне замовлення: {current}");
        Console.WriteLine("1 — Створити замовлення");
        Console.WriteLine("2 — Додати рядок");
        Console.WriteLine("3 — Застосувати знижку (політика обсягу)");
        Console.WriteLine("4 — Показати підсумок (з ПДВ)");
        Console.WriteLine("5 — Показати замовлення");
        Console.WriteLine("0 — Вихід");
        Console.Write("> ");
    }

    private void CreateOrder()
    {
        Console.Write("Customer Id: ");
        Result<int> idResult = InputParsers.ParseInt(Console.ReadLine(), "Customer Id");
        if (idResult.IsFailure)
        {
            Console.WriteLine(idResult.Error);
            return;
        }

        Console.Write("Full name: ");
        string? name = Console.ReadLine();
        Console.Write("Email: ");
        string? email = Console.ReadLine();

        Result<int> created = this._orderService.CreateOrder(
            new CreateOrderRequest(idResult.Value, name ?? string.Empty, email ?? string.Empty));

        if (created.IsFailure)
        {
            Console.WriteLine($"Помилка: {created.Error}");
            return;
        }

        this._currentOrderId = created.Value;
        Console.WriteLine($"Створено замовлення № {created.Value}");
    }

    private void AddLine()
    {
        if (!this.TryGetCurrentOrderId(out int orderId))
        {
            return;
        }

        Console.Write("Product name: ");
        string? product = Console.ReadLine();

        Console.Write("Quantity: ");
        Result<int> qtyResult = InputParsers.ParseInt(Console.ReadLine(), "Quantity");
        if (qtyResult.IsFailure)
        {
            Console.WriteLine(qtyResult.Error);
            return;
        }

        Console.Write("Unit price (decimal, e.g. 199.99): ");
        Result<decimal> priceResult = InputParsers.ParseDecimal(Console.ReadLine(), "Unit price");
        if (priceResult.IsFailure)
        {
            Console.WriteLine(priceResult.Error);
            return;
        }

        Result addResult = this._orderService.AddLine(
            new AddOrderLineRequest(orderId, product ?? string.Empty, qtyResult.Value, priceResult.Value));

        Console.WriteLine(addResult.IsSuccess ? "Рядок додано." : $"Помилка: {addResult.Error}");
    }

    private void ApplyDiscount()
    {
        if (!this.TryGetCurrentOrderId(out int orderId))
        {
            return;
        }

        Result<decimal> result = this._orderService.ApplyPolicyDiscount(new ApplyDiscountRequest(orderId));
        if (result.IsFailure)
        {
            Console.WriteLine($"Помилка: {result.Error}");
            return;
        }

        Console.WriteLine($"Застосовано знижку: {result.Value:P0}");
    }

    private void PrintTotals()
    {
        if (!this.TryGetCurrentOrderId(out int orderId))
        {
            return;
        }

        Result<OrderTotals> totalsResult = this._orderService.GetTotals(orderId);
        if (totalsResult.IsFailure)
        {
            Console.WriteLine($"Помилка: {totalsResult.Error}");
            return;
        }

        OrderTotals t = totalsResult.Value;
        Console.WriteLine("--- Підсумок ---");
        Console.WriteLine($"Subtotal:          {t.Subtotal}");
        Console.WriteLine($"Discount:          {t.DiscountAmount}");
        Console.WriteLine($"Net after disc.:   {t.NetAfterDiscount}");
        Console.WriteLine($"VAT ({FinancialConstants.VatRate:P0}):      {t.VatAmount}");
        Console.WriteLine($"Grand total:       {t.GrandTotal}");
    }

    private void ShowOrder()
    {
        if (!this.TryGetCurrentOrderId(out int orderId))
        {
            return;
        }

        Result<Order> orderResult = this._orderService.GetOrder(orderId);
        if (orderResult.IsFailure)
        {
            Console.WriteLine($"Помилка: {orderResult.Error}");
            return;
        }

        Order order = orderResult.Value;
        Console.WriteLine($"Order #{order.Id} | {order.Status} | {order.Customer.FullName} <{order.Customer.Email}>");
        Console.WriteLine($"Discount: {order.AppliedDiscount}");
        foreach (OrderLine line in order.Lines)
        {
            Console.WriteLine($"  - {line.ProductName}: {line.Quantity} × {line.UnitPrice} = {line.LineTotal}");
        }
    }

    private bool TryGetCurrentOrderId(out int orderId)
    {
        if (this._currentOrderId is null)
        {
            Console.WriteLine("Спочатку створіть замовлення (пункт 1).");
            orderId = 0;
            return false;
        }

        orderId = this._currentOrderId.Value;
        return true;
    }
}
