# Архітектура ShopOrders (СР3)

## 1. Схема залежностей проєктів

```
ShopOrders.App ──► ShopOrders.Core
ShopOrders.Tests ──► ShopOrders.Core
```

`Core` не залежить від `App`. Тести не залежать від `App`.

## 2. Шари всередині Core

| Шар | Простір імен | Призначення |
|-----|--------------|-------------|
| Domain | `ShopOrders.Core.Domain` | сутності, інваріанти, політики |
| Application | `ShopOrders.Core.Application` | `OrderService`, `Result`, парсери |
| Infrastructure | `ShopOrders.Core.Infrastructure` | `InMemoryOrderRepository` |

## 3. Точки розширення без ламання шарів

1. Нова знижка — нова реалізація `IDiscountPolicy`.
2. Інше сховище — нова реалізація `IOrderRepository`.
3. Інший UI — новий хост замість `ShopOrders.App`.

## 4. Рисунок 1 (текстова схема)

```
[ConsoleUi/Program] → [OrderService] → [IDiscountPolicy]
                            ↓
                    [IOrderRepository]
                            ↓
                      [Order aggregate]
```
