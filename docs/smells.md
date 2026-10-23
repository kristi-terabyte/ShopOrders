# Реєстр запахів коду (ЛР6)

Модуль: `Order` + `OrderService` + політики знижок.

| # | Запах | Де було | Рефакторинг | Статус | Вимірювання |
|---|-------|---------|-------------|--------|-------------|
| 1 | Long Method | розрахунок підсумку | Extract Method → `SumLineTotals`, `CalculateVat` | усунуто | LOC / CC у `metrics.md` |
| 2 | Magic Number | `0.2`, `0.05`, `1000` | `FinancialConstants` | усунуто | grep літералів |
| 3 | Primitive Obsession | «голі» decimal/string | `Money`, `Discount`, `Customer` | усунуто | типи в Domain |
| 4 | Feature Envy / UI в домені | друк у розрахунку | `ConsoleUi` | усунуто | відсутність Console у Core |
| 5 | Shotgun Surgery (політики) | if-и знижок у сервісі | `IDiscountPolicy` | усунуто | одна точка розширення |
| 6 | Data Class | публічні set-ери | інкапсуляція `Order` | усунуто | лише методи переходів |
| 7 | Silent failure | `int.Parse` | `InputParsers` + `Result` | усунуто | тести парсерів |
| 8 | Duplicated Code (ризик сум) | повтор ПДВ/знижки | спільні value objects | усунуто | один `CalculateVat` |

## Залишок

In-memory репозиторій — прийнятний для навчального консольного сценарію (`tech-debt.md`).
