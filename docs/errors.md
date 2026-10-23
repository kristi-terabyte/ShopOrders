# Класифікація помилок ShopOrders (ЛР5)

| # | Ситуація | Клас | Як повідомляємо | Де в коді |
|---|----------|------|-----------------|-----------|
| 1 | Порожнє ім’я клієнта | Помилка користувача | `Result.Failure` / виняток ctor | `Customer` |
| 2 | Email без `@` | Помилка користувача | `ArgumentException` | `Customer` |
| 3 | Кількість ≤ 0 | Помилка користувача | `ArgumentOutOfRangeException` | `OrderLine` |
| 4 | Від’ємна ціна / сума | Помилка користувача | `ArgumentOutOfRangeException` | `Money` |
| 5 | Неможливий парсинг числа з консолі | Помилка користувача | `Result.Failure` | `InputParsers` |
| 6 | Підтвердження порожнього замовлення | Помилка користувача / домен | `InvalidOperationException` | `Order.Confirm` |
| 7 | Додавання рядка не в `New` | Порушення інваріанту | `InvalidOperationException` | `Order.EnsureEditable` |
| 8 | Скасування після `Shipped` | Порушення інваріанту | `InvalidOperationException` | `Order.Cancel` |
| 9 | Збій інфраструктури сховища (майбутнє) | Системна | лог Error + виняток | `IOrderRepository` (заглушка in-memory) |
