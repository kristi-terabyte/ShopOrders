using Microsoft.Extensions.Logging;
using ShopOrders.App;
using ShopOrders.Core;
using ShopOrders.Core.Application;
using ShopOrders.Core.Domain;
using ShopOrders.Core.Infrastructure;

using ILoggerFactory loggerFactory = LoggerFactory.Create(builder =>
{
    builder
        .AddSimpleConsole(options =>
        {
            options.SingleLine = true;
            options.TimestampFormat = "HH:mm:ss ";
        })
        .SetMinimumLevel(LogLevel.Information);
});

ILogger<OrderService> orderLogger = loggerFactory.CreateLogger<OrderService>();
ILogger<ConsoleUi> uiLogger = loggerFactory.CreateLogger<ConsoleUi>();

IOrderRepository repository = new InMemoryOrderRepository();
IDiscountPolicy discountPolicy = new VolumeDiscountPolicy();
OrderService orderService = new(repository, discountPolicy, orderLogger);

ConsoleUi ui = new(orderService, uiLogger);
ui.Run();
