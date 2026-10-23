# ShopOrders

Навчальний варіант №1 — облік замовлень інтернет-магазину.  
Курс: **Конструювання ПЗ**.  
Виконавець: студент групи (варіант 1).

Локальний репозиторій (віддалений GitHub remote не задано як «справжній» URL).

## Структура

```
ShopOrders.sln
src/ShopOrders.Core/     # Domain / Application / Infrastructure
src/ShopOrders.App/      # консольний UI
tests/ShopOrders.Tests/  # xUnit + fakes
docs/                    # стандарти, метрики, аудит
reports/                 # заготовки звітів LR/SR
.github/workflows/ci.yml
```

## Вимоги

- .NET SDK 8+ (збірка цілить `net8.0`)
- (опційно) Git

## Команди

```bash
dotnet restore
dotnet build -c Release
dotnet test -c Release
dotnet run --project src/ShopOrders.App -c Release
```

Покриття (coverlet collector):

```bash
dotnet test -c Release --collect:"XPlat Code Coverage"
```

## Що вміє консоль

1. Створити замовлення (клієнт з інваріантами)
2. Додати рядки товарів
3. Застосувати знижку за політикою обсягу (≥ 1000 UAH → 5 %)
4. Показати підсумок: subtotal, discount, VAT 20 %, grand total (`decimal`)

## Ключові правила домену

| Правило | Реалізація |
|--------|------------|
| Гроші лише `decimal` | `Money`, `FinancialConstants.VatRate = 0.20m` |
| Округлення до 2 знаків | `MidpointRounding.AwayFromZero` |
| Інваріанти | `Order`, `OrderLine`, `Customer`, `Discount`/`Money` |
| SOLID | `IDiscountPolicy`, `IOrderRepository`, DI у `Program` |

## Версія

Див. `ShopOrders.Core.VersionInfo` (`1.0.0`).
