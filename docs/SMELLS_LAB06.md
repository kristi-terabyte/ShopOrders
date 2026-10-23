# Реєстр запахів коду (LR6)

**Модуль після рефакторингу:** `Order` + `OrderService` + політики знижок.

| # | Запах | Де було | Рефакторинг | Статус |
|---|-------|---------|-------------|--------|
| 1 | Long Method | розрахунок підсумку | Extract Method → `SumLineTotals`, `CalculateVat` | усунуто |
| 2 | Magic Number | `0.2`, `0.05`, `1000` | `FinancialConstants` | усунуто |
| 3 | Primitive Obsession | `decimal` / `string` всюди | `Money`, `Discount`, `Customer` | усунуто |
| 4 | Feature Envy / UI в домені | друк у розрахунку | консоль у `ConsoleUi` | усунуто |
| 5 | Shotgun Surgery (політики) | if-и знижок у сервісі | `IDiscountPolicy` | усунуто |
| 6 | Data Class | публічні set-ери рядків | інкапсуляція `Order` | усунуто |
| 7 | Silent failure | `int.Parse` | `InputParsers` + `Result` | усунуто |
| 8 | God Class (ризик) | усе в Program | шари Domain/Application/Infrastructure | зменшено |

## Залишок

- In-memory репозиторій — прийнятний для навчального консольного сценарію (зафіксовано в аудиті SR2).
