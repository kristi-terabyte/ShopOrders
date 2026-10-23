# Стандарт кодування ShopOrders (SR1)

**Проєкт:** ShopOrders (варіант №1)  
**Курс:** Конструювання ПЗ  
**Виконавець:** студент групи (варіант 1)

## 1. Мета

Єдині правила іменування, форматування, типів і документації для всього семестрового репозиторію. Частина правил закріплена в `.editorconfig`, `stylecop.json` і `Directory.Build.props` (збірка з 0 попереджень).

## 2. Іменування

| Елемент | Правило | Приклад |
|--------|---------|---------|
| Типи, методи, властивості | PascalCase | `OrderService`, `CalculateTotals` |
| Параметри, локальні | camelCase | `unitPrice`, `orderId` |
| Приватні поля | `_camelCase` | `_repository`, `_lines` |
| Інтерфейси | префікс `I` | `IDiscountPolicy` |
| Сталі | PascalCase | `VatRate` |

Ідентифікатори коду — **англійською**. Коментарі та docs — українською/англійською.

## 3. Гроші, знижки, ПДВ (акцент ShopOrders)

1. **Заборонено** `double` / `float` для сум, ставок ПДВ і знижок.
2. Використовувати `decimal` і тип `Money`.
3. Ставка ПДВ — іменована стала `FinancialConstants.VatRate = 0.20m` (не «магічне» `0.2`).
4. Округлення грошових сум — **2 знаки**, `MidpointRounding.AwayFromZero`.
5. Знижка — частка `0..0.50` у типі `Discount`; застосування через `Discount.ApplyTo(Money)`.
6. Порядок розрахунку: **рядки → знижка → ПДВ → grand total**.

### Антиприклади

```csharp
// ПОГАНО
double total = qty * price * 1.2;

// ДОБРЕ
Money net = discount.ApplyTo(subtotal);
Money vat = new Money(net.Amount * FinancialConstants.VatRate);
```

## 4. XML-документація

Усі публічні типи й члени `ShopOrders.Core` мають XML-коментарі (`///`). Увімкнено `GenerateDocumentationFile`.

## 5. Контракти й помилки

- `ArgumentNullException.ThrowIfNull`, `ArgumentException.ThrowIfNullOrWhiteSpace`.
- Парсинг введення — `TryParse` + `Result` (`InputParsers`), без «німого» `int.Parse`.
- Доменні порушення стану — `InvalidOperationException` / `DomainException`.
- Прикладні команди повертають `Result` / `Result<T>`.

## 6. Шари

```
App (UI) → Application → Domain
                ↓
          Infrastructure
```

Залежності спрямовані всередину до Domain. UI не містить формул ПДВ.

## 7. Тести

- xUnit, принципи FIRST.
- Дублі: `FakeOrderRepository`, `NullLogger<T>`.
- Обов’язкове покриття: `VolumeDiscountPolicy`, `OrderService`.

## 8. Машинне закріплення

| Файл | Роль |
|------|------|
| `.editorconfig` | стиль, іменування |
| `stylecop.json` | StyleCop |
| `Directory.Build.props` | analyzers, TreatWarningsAsErrors |
| `.github/workflows/ci.yml` | build + test |
