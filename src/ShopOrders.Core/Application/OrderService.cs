using Microsoft.Extensions.Logging;
using ShopOrders.Core.Domain;

namespace ShopOrders.Core.Application;

/// <summary>
/// Прикладний сервіс обліку замовлень (команди / запити розділені за CQS).
/// </summary>
public sealed class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly IDiscountPolicy _discountPolicy;
    private readonly ILogger<OrderService> _logger;
    private int _nextOrderId = 1;

    /// <summary>
    /// Створює сервіс із впровадженням залежностей.
    /// </summary>
    /// <param name="repository">Сховище.</param>
    /// <param name="discountPolicy">Політика знижок.</param>
    /// <param name="logger">Логер.</param>
    public OrderService(
        IOrderRepository repository,
        IDiscountPolicy discountPolicy,
        ILogger<OrderService> logger)
    {
        ArgumentNullException.ThrowIfNull(repository);
        ArgumentNullException.ThrowIfNull(discountPolicy);
        ArgumentNullException.ThrowIfNull(logger);

        this._repository = repository;
        this._discountPolicy = discountPolicy;
        this._logger = logger;
    }

    /// <summary>
    /// Команда: створити замовлення.
    /// </summary>
    /// <param name="request">Дані клієнта.</param>
    /// <returns>Result з ідентифікатором замовлення.</returns>
    public Result<int> CreateOrder(CreateOrderRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);

        try
        {
            Customer customer = new(request.CustomerId, request.CustomerName, request.CustomerEmail);
            int orderId = this._nextOrderId++;
            Order order = new(orderId, customer);
            this._repository.Save(order);

            this._logger.LogInformation(
                "Created order {OrderId} for customer {CustomerId}",
                orderId,
                customer.Id);

            return Result.Success(orderId);
        }
        catch (ArgumentException ex)
        {
            this._logger.LogWarning(ex, "Validation failed while creating order");
            return Result.Failure<int>(ex.Message);
        }
    }

    /// <summary>
    /// Команда: додати рядок до замовлення.
    /// </summary>
    /// <param name="request">Дані рядка.</param>
    /// <returns>Result.</returns>
    public Result AddLine(AddOrderLineRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);

        Order? order = this._repository.GetById(request.OrderId);
        if (order is null)
        {
            return Result.Failure($"Order {request.OrderId} was not found.");
        }

        try
        {
            OrderLine line = new(request.ProductName, request.Quantity, new Money(request.UnitPrice));
            order.AddLine(line);
            this._repository.Save(order);

            this._logger.LogInformation(
                "Added line {Product} x{Qty} to order {OrderId}",
                request.ProductName,
                request.Quantity,
                request.OrderId);

            return Result.Success();
        }
        catch (ArgumentException ex)
        {
            this._logger.LogWarning(ex, "Invalid line for order {OrderId}", request.OrderId);
            return Result.Failure(ex.Message);
        }
        catch (InvalidOperationException ex)
        {
            this._logger.LogWarning(ex, "Cannot modify order {OrderId}", request.OrderId);
            return Result.Failure(ex.Message);
        }
    }

    /// <summary>
    /// Команда: застосувати знижку згідно з політикою.
    /// </summary>
    /// <param name="request">Запит.</param>
    /// <returns>Result зі ставкою знижки.</returns>
    public Result<decimal> ApplyPolicyDiscount(ApplyDiscountRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);

        Order? order = this._repository.GetById(request.OrderId);
        if (order is null)
        {
            return Result.Failure<decimal>($"Order {request.OrderId} was not found.");
        }

        try
        {
            OrderTotals preview = order.CalculateTotals();
            Discount discount = this._discountPolicy.Resolve(preview.Subtotal);
            order.ApplyDiscount(discount);
            this._repository.Save(order);

            this._logger.LogInformation(
                "Applied discount {Rate} to order {OrderId}",
                discount.Rate,
                request.OrderId);

            return Result.Success(discount.Rate);
        }
        catch (InvalidOperationException ex)
        {
            this._logger.LogWarning(ex, "Cannot apply discount to order {OrderId}", request.OrderId);
            return Result.Failure<decimal>(ex.Message);
        }
    }

    /// <summary>
    /// Запит: підсумки замовлення (без зміни стану).
    /// </summary>
    /// <param name="orderId">Ідентифікатор.</param>
    /// <returns>Result з підсумками.</returns>
    public Result<OrderTotals> GetTotals(int orderId)
    {
        Order? order = this._repository.GetById(orderId);
        if (order is null)
        {
            return Result.Failure<OrderTotals>($"Order {orderId} was not found.");
        }

        OrderTotals totals = order.CalculateTotals();
        this._logger.LogDebug("Calculated totals for order {OrderId}: {GrandTotal}", orderId, totals.GrandTotal);
        return Result.Success(totals);
    }

    /// <summary>
    /// Запит: отримати замовлення.
    /// </summary>
    /// <param name="orderId">Ідентифікатор.</param>
    /// <returns>Result з Order.</returns>
    public Result<Order> GetOrder(int orderId)
    {
        Order? order = this._repository.GetById(orderId);
        if (order is null)
        {
            return Result.Failure<Order>($"Order {orderId} was not found.");
        }

        return Result.Success(order);
    }
}
