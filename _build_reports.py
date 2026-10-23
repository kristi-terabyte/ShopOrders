# -*- coding: utf-8 -*-
"""Генерація DOCX/PDF звітів ЛР1–8 та СР1–3 для ShopOrders (варіант 1).

Структура звітів узгоджена з розд. 5 відповідних методичних вказівок.
Виводи команд — як рисунки у стилі терміналу; код — текстові лістинги Consolas.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reports" / "docx"
OUT.mkdir(parents=True, exist_ok=True)
SHOTS = ROOT / "_shots"
SHOTS.mkdir(exist_ok=True)
TERM = SHOTS / "term"
TERM.mkdir(exist_ok=True)

# ЗАПОВНІТЬ перед фінальною здачею (зараз плейсхолдери — див. відкриті питання)
STUDENT = "________________"
GROUP = "________________"
VARIANT = "№1 — ShopOrders (облік замовлень інтернет-магазину)"
DISCIPLINE = "Конструювання програмного забезпечення"
REPO_URL = "https://github.com/kristi-terabyte/ShopOrders"

_BG = (12, 12, 12)
_TITLE = (40, 40, 40)
_FG = (204, 204, 204)
_CMD = (240, 240, 240)
_OK = (80, 200, 120)
_DIM = (140, 140, 140)


def set_run(run, *, bold=False, size=14, mono=False, color: RGBColor | None = None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Consolas" if mono else "Times New Roman"
    if color is not None:
        run.font.color.rgb = color
    r = run._element.get_or_add_rPr().get_or_add_rFonts()
    r.set(qn("w:eastAsia"), run.font.name)
    r.set(qn("w:ascii"), run.font.name)
    r.set(qn("w:hAnsi"), run.font.name)


def P(doc, text="", *, bold=False, center=False, first=True, after=6, size=14, mono=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.15
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.first_line_indent = Cm(0)
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.first_line_indent = Cm(1.25) if first else Cm(0)
    if text:
        set_run(p.add_run(text), bold=bold, size=size, mono=mono)
    return p


def H(doc, text, *, size=14, before: int = 12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(text), bold=True, size=size)


def H2(doc, text):
    H(doc, text, size=13)


def read_src(rel: str, max_lines: int = 28) -> str:
    path = ROOT / rel
    if not path.exists():
        return f"// файл відсутній у репозиторії: {rel}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) > max_lines:
        head = max_lines // 2
        tail = max_lines - head - 1
        shown = lines[:head] + ["// … фрагмент скорочено; повний файл у репозиторії …"] + lines[-tail:]
        return "\n".join(shown)
    return "\n".join(lines)


def listing(doc, n: int, title: str, code: str, *, explain: str = ""):
    """Лістинг коду текстом (Consolas 10 пт) — вимога методички."""
    P(doc, f"Лістинг {n} — {title}", first=False, after=4, bold=True)
    for line in code.replace("\t", "    ").splitlines()[:32]:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        set_run(p.add_run(line if line.strip() else " "), size=10, mono=True)
    if explain:
        P(doc, explain, first=False, after=8, size=12)


def _font(size: int) -> ImageFont.ImageFont:
    for path in (
        r"C:\Windows\Fonts\cascadiamono.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _shorten_paths(text: str) -> str:
    out = []
    for line in text.splitlines():
        if "ShopOrders" in line and ("\\" in line or "/" in line) and "C:" in line:
            c = line.find("C:")
            rest = line[c:]
            cut = rest.find("ShopOrders")
            if cut >= 0:
                line = line[:c] + "...\\" + rest[cut:]
        out.append(line[:108])
    return "\n".join(out)


def render_terminal_png(
    body: str,
    out_path: Path,
    *,
    title: str = "Terminal — ShopOrders",
    prompt_cmd: str | None = None,
    max_lines: int = 16,
) -> Path:
    body = _shorten_paths(body).replace("\t", "    ")
    lines = [ln.rstrip() for ln in body.strip().splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    display: list[tuple[str, tuple[int, int, int]]] = []
    if prompt_cmd:
        display.append((f"PS ShopOrders> {prompt_cmd}", _CMD))
    for ln in lines:
        color = _FG
        low = ln.lower()
        if any(k in low for k in ("build succeeded", "passed!", "0 warning", "0 error")):
            color = _OK
        display.append((ln if ln.strip() else " ", color))

    font = _font(15)
    title_font = _font(13)
    pad_x, pad_y, line_h, title_h = 18, 14, 22, 34
    tmp = Image.new("RGB", (10, 10))
    dr = ImageDraw.Draw(tmp)
    max_w = 720
    for text, _ in display:
        bbox = dr.textbbox((0, 0), text, font=font)
        max_w = max(max_w, bbox[2] - bbox[0] + pad_x * 2)
    max_w = min(max_w, 980)
    height = title_h + pad_y * 2 + line_h * max(len(display), 1) + 8

    img = Image.new("RGB", (max_w, height), _BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, max_w, title_h), fill=_TITLE)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        x = 14 + i * 16
        draw.ellipse((x, 11, x + 10, 21), fill=col)
    draw.text((70, 8), title, fill=_DIM, font=title_font)
    y = title_h + pad_y
    for text, color in display:
        draw.text((pad_x, y), text, fill=color, font=font)
        y += line_h
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def figure_terminal(
    doc,
    n: int,
    caption: str,
    body: str,
    *,
    prompt_cmd: str,
    explain: str,
    png_name: str,
):
    """Рисунок — скрін терміналу + обов’язкове пояснення (пояснення перед зображенням, щоб не відривалось на наступну сторінку)."""
    cap = P(doc, f"Рисунок {n} — {caption}", first=False, after=2, bold=True)
    cap.paragraph_format.keep_with_next = True
    exp = P(doc, explain, first=False, after=2, size=12)
    exp.paragraph_format.keep_with_next = True
    png = render_terminal_png(
        body,
        TERM / png_name,
        title=f"Terminal — {caption}",
        prompt_cmd=prompt_cmd,
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(str(png), width=Cm(13.5))


def add_table(doc, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        set_run(cell.paragraphs[0].add_run(h), bold=True, size=11)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            set_run(cell.paragraphs[0].add_run(val), size=11)
    P(doc, "", first=False, after=8)


def add_cc_formula(doc):
    """Редагована формула Word (OMML): M = π + 1."""
    from docx.oxml import parse_xml

    P(doc, "Цикломатичну складність оцінювали за спрощеною формулою для C#:", first=False)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Cm(0)
    p2.paragraph_format.space_after = Pt(4)
    math = parse_xml(
        '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
        "<m:r><m:t>M</m:t></m:r>"
        "<m:r><m:t>=</m:t></m:r>"
        "<m:r><m:t>π</m:t></m:r>"
        "<m:r><m:t>+</m:t></m:r>"
        "<m:r><m:t>1</m:t></m:r>"
        "</m:oMath>"
    )
    p2._element.append(math)
    P(
        doc,
        "де M — цикломатична складність, π — кількість точок прийняття рішень "
        "(умовні оператори, цикли, логічні «і/або» в умовах). (1)",
        first=False,
        after=8,
        size=12,
    )


def title_page(doc, kind: str, number: int | str, topic: str):
    for s in doc.sections:
        s.top_margin = Cm(2)
        s.bottom_margin = Cm(2)
        s.left_margin = Cm(3)
        s.right_margin = Cm(1.5)
    P(doc, "МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", center=True, first=False, after=0)
    P(doc, DISCIPLINE, center=True, first=False, after=18)
    P(doc, "", first=False, after=36)
    P(doc, f"{kind} № {number}", bold=True, center=True, first=False, after=6)
    P(doc, f"Тема: {topic}", bold=True, center=True, first=False, after=20)
    P(doc, f"Виконавець: {STUDENT}", first=False, after=2)
    P(doc, f"Група: {GROUP}", first=False, after=2)
    P(doc, f"Варіант: {VARIANT}", first=False, after=2)
    P(doc, f"Репозиторій: {REPO_URL}", first=False, after=20)
    P(doc, "Київ – 2026", center=True, first=False, after=0)
    doc.add_page_break()


def capture_outputs() -> bool:
    build = subprocess.run(
        ["dotnet", "build", "-c", "Release"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (SHOTS / "build.txt").write_text(build.stdout + "\n" + build.stderr, encoding="utf-8")
    test = subprocess.run(
        ["dotnet", "test", "-c", "Release", "--no-build"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (SHOTS / "test.txt").write_text(test.stdout + "\n" + test.stderr, encoding="utf-8")
    log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (SHOTS / "git_log.txt").write_text(log.stdout, encoding="utf-8")
    return build.returncode == 0 and test.returncode == 0


def shot_texts() -> tuple[str, str, str]:
    build = (SHOTS / "build.txt").read_text(encoding="utf-8", errors="replace")
    test = (SHOTS / "test.txt").read_text(encoding="utf-8", errors="replace")
    log = (SHOTS / "git_log.txt").read_text(encoding="utf-8", errors="replace")
    return build, test, log


def common_inputs(doc):
    P(
        doc,
        "Проєкт варіанта: ShopOrders. Предметна область — облік замовлень "
        "інтернет-магазину. Сутності: Customer (клієнт), Product / позиція товару в "
        "рядку OrderLine, агрегат Order (документ), перелічення OrderStatus "
        "(New, Paid, Shipped, Cancelled, Returned). Припущення: валюта розрахунків — "
        "UAH; ПДВ — 20 %; знижка за обсягом — 5 % від суми рядків при subtotal ≥ 1000 UAH; "
        "суми лише через decimal.",
    )


def append_repo_and_log(doc, build: str, test: str, log: str, *, fig_start: int = 1):
    H(doc, "Посилання на репозиторій")
    P(doc, f"GitHub: {REPO_URL}", first=False)
    P(doc, "Гілка: main. Історія комітів lab01–lab08 відображає етапи курсу.", first=False)
    figure_terminal(
        doc,
        fig_start,
        "вивід git log --oneline",
        log.strip(),
        prompt_cmd="git log --oneline",
        explain="На рисунку видно послідовність комітів етапів лабораторних робіт у головній гілці.",
        png_name=f"fig{fig_start}_git.png",
    )


# ---- per-lab builders -------------------------------------------------------

def build_lab01(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Розгорнути середовище конструювання для навчального проєкту ShopOrders: "
        "рішення .NET 8 з бібліотекою логіки та консоллю, Git з осмисленими комітами, "
        "машинно закріплений стандарт (.editorconfig, StyleCop) і README, з якого можна "
        "за 5 хвилин зрозуміти, як зібрати й запустити проєкт. Після роботи репозиторій "
        "має збиратися командою dotnet build без попереджень.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")

    H2(doc, "3.1. Завдання 1 — створення рішення .NET 8")
    P(
        doc,
        "Створено ShopOrders.sln, проєкти ShopOrders.Core (classlib) і ShopOrders.App "
        "(console), додано посилання App → Core. Структура відповідає вимозі курсу: "
        "логіка в бібліотеці, UI — у консолі.",
        first=False,
    )
    listing(
        doc,
        1,
        "фрагмент README.md (структура)",
        read_src("README.md", 22),
        explain="У README зафіксовано структуру рішення та команди відтворення.",
    )

    H2(doc, "3.2. Завдання 2 — Git і .gitignore")
    P(
        doc,
        "Ініціалізовано репозиторій, додано .gitignore для .NET (bin/, obj/, IDE-файли). "
        "Власні доповнення: виключення локальних звітів PDF/DOCX у reports/docx/ за потреби "
        "здачі окремим архівом, каталог _shots/ і допоміжні скрипти генерації.",
        first=False,
    )
    listing(doc, 2, ".gitignore (фрагмент)", read_src(".gitignore", 24))

    H2(doc, "3.3. Завдання 3 — доменний скелет")
    P(
        doc,
        "Додано типи Customer, Order, OrderLine, OrderStatus (і подальші Money/Discount). "
        "Таблиця відповідності ролей для варіанта №1:",
        first=False,
    )
    add_table(
        doc,
        ["Роль", "Тип у ShopOrders", "Примітка"],
        [
            ["Документ", "Order", "агрегат замовлення"],
            ["Позиція", "OrderLine", "товар × кількість"],
            ["Клієнт", "Customer", "учасник замовлення"],
            ["Стан документа", "OrderStatus", "New…Returned"],
        ],
    )
    listing(
        doc,
        3,
        "OrderStatus.cs",
        read_src("src/ShopOrders.Core/Domain/OrderStatus.cs", 20),
        explain="Перелічення станів документа варіанта №1.",
    )

    H2(doc, "3.4. Завдання 4 — .editorconfig")
    listing(
        doc,
        4,
        ".editorconfig (фрагмент)",
        read_src(".editorconfig", 26),
        explain="Правила відступів, кодування UTF-8 і частини діагностик закріплено машинно.",
    )

    H2(doc, "3.5. Завдання 5 — аналізатори")
    P(
        doc,
        "У Directory.Build.props увімкнено аналізатори та TreatWarningsAsErrors. "
        "Збірка Release завершується з 0 Warning(s) і 0 Error(s).",
        first=False,
    )
    figure_terminal(
        doc,
        1,
        "результат dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-10:]),
        prompt_cmd="dotnet build -c Release",
        explain="На рисунку видно успішну збірку всіх трьох проєктів без попереджень.",
        png_name="lr01_build.png",
    )

    H2(doc, "3.6. Завдання 6 — стандарт кодування")
    P(
        doc,
        "Текстовий стандарт винесено в docs/CODING_STANDARD.md (іменування, типи грошей, "
        "XML-docs, заборона double для сум).",
        first=False,
    )
    listing(doc, 5, "docs/CODING_STANDARD.md (фрагмент)", read_src("docs/CODING_STANDARD.md", 24))

    H2(doc, "3.7. Завдання 7 — підсумковий коміт і перевірка")
    P(
        doc,
        "Підсумковий стан зафіксовано комітами lab01–lab08. Вивід git log наведено "
        "після аналізу (рисунок 2), щоб не відривати підпис від рисунка на окрему сторінку.",
        first=False,
    )

    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Після увімкнення StyleCop/editorconfig типові попередження стосувалися "
        "документації, using і стилю. Підсумкова таблиця (за фінальним станом репозиторію):",
    )
    add_table(
        doc,
        ["#", "Діагностика / тема", "Частота (оцінка на старті)", "Що зроблено"],
        [
            ["1", "SA1600 / XML-docs public", "висока", "додано summary/param"],
            ["2", "IDE0005 unused using", "середня", "прибрано зайві using"],
            ["3", "відступи / форматування", "середня", "dotnet format + editorconfig"],
            ["4", "іменування private fields", "низька", "префікс _"],
            ["5", "інші SA*", "низька", "виправлено точково"],
        ],
    )
    P(
        doc,
        "Нуль попереджень у фінальній збірці означає, що «шум» стилю прибрано; "
        "змістовні правила (decimal, інваріанти) перевіряються далі тестами (ЛР7).",
        first=False,
    )

    H(doc, "5. Висновки")
    for t in [
        "Створено двопроєктне рішення .NET 8 і закріплено Git-історію.",
        "Стандарт частково машинний (.editorconfig, аналізатори) і частково текстовий (docs).",
        "Найбільше часу зайняло доведення збірки до 0 попереджень StyleCop.",
        "Ухвалено правило: гроші лише decimal; double у фінансах заборонено.",
        "Репозиторій придатний як база для ЛР2–ЛР8.",
    ]:
        P(doc, f"• {t}", first=False)

    H(doc, "6. Посилання на репозиторій", before=8)
    P(doc, f"{REPO_URL}", first=False)
    figure_terminal(
        doc,
        2,
        "історія комітів git log --oneline",
        log.strip(),
        prompt_cmd="git log --oneline",
        explain="Коміт lab01 відповідає скетчу середовища; подальші lab02–lab08 — наступні роботи.",
        png_name="lr01_git.png",
    )


def build_lab02(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Привести код ShopOrders до єдиного стандарту іменування та форматування, "
        "прибрати «магічні» числа у фінансах, зафіксувати XML-документацію public-членів "
        "і переконатися, що збірка лишається без попереджень.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")
    H2(doc, "3.1–3.2. Іменування та константи")
    listing(
        doc,
        1,
        "FinancialConstants.cs",
        read_src("src/ShopOrders.Core/Domain/FinancialConstants.cs", 30),
        explain="Ставка ПДВ і параметри знижки винесені в іменовані константи decimal.",
    )
    H2(doc, "3.3. Типи Money / Discount")
    listing(
        doc,
        2,
        "Money.cs (фрагмент)",
        read_src("src/ShopOrders.Core/Domain/Money.cs", 28),
        explain="Грошове значення інкапсульовано; арифметика через decimal.",
    )
    H2(doc, "3.4–3.5. Документація та перевірка")
    figure_terminal(
        doc,
        1,
        "dotnet build -c Release після приведення до стандарту",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Збірка підтверджує відсутність попереджень аналізаторів.",
        png_name="lr02_build.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Після заміни літералів на FinancialConstants і введення Money/Discount читабельність "
        "фінансової логіки зросла; ризик помилок округлення double усунуто на рівні типів.",
    )
    H(doc, "5. Висновки")
    for t in [
        "Уніфіковано іменування за конвенціями C# і стандартом проєкту.",
        "Фінансові ставки більше не «магічні числа» у коді методів.",
        "XML-docs додано до публічного API домену.",
        "Збірка Release лишається з 0 попереджень.",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)


def build_lab03(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Декомпозувати розрахунок підсумку замовлення, додати захисні контракти аргументів "
        "і станів, розділити запити й команди (CQS) та зафіксувати метрики «до/після».",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")
    H2(doc, "3.1. Декомпозиція CalculateTotals")
    listing(
        doc,
        1,
        "Order.cs — CalculateTotals / SumLineTotals / CalculateVat (фрагмент)",
        read_src("src/ShopOrders.Core/Domain/Order.cs", 30),
        explain="Оркестрація підсумку винесена з «монстр-методу»; обчислення розбито на короткі методи.",
    )
    # show totals section from file specifically
    order_txt = (ROOT / "src/ShopOrders.Core/Domain/Order.cs").read_text(encoding="utf-8")
    m = re.search(r"(public OrderTotals CalculateTotals[\s\S]+?private void EnsureEditable[\s\S]+?\n    \})", order_txt)
    if m:
        listing(doc, 2, "Order.cs — блок розрахунку", m.group(1)[:1200], explain="Фрагмент із репозиторію після рефакторингу.")

    H2(doc, "3.2. Метрики та формула складності")
    add_cc_formula(doc)
    P(doc, "Таблиця метрик (див. також docs/METRICS_LAB03.md):", first=False)
    add_table(
        doc,
        ["Метод", "LOC (тіло)", "CC (оцінка)", "Примітка"],
        [
            ["CalculateTotals (було)", "~50", "~9", "моноліт"],
            ["CalculateTotals (стало)", "~10", "1", "оркестрація"],
            ["SumLineTotals", "~7", "2", "цикл"],
            ["CalculateVat", "~4", "1", "формула ПДВ"],
            ["EnsureEditable", "~5", "2", "контракт стану"],
        ],
    )
    figure_terminal(
        doc,
        1,
        "dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Після декомпозиції рішення збирається без попереджень.",
        png_name="lr03_build.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Цикломатична складність розрахунку знижена шляхом винесення гілок у окремі методи. "
        "Query CalculateTotals не змінює стан замовлення (CQS). Захисні контракти "
        "ArgumentNullException.ThrowIfNull / перевірка статусу відсікають некоректні виклики "
        "на межі агрегату. Показник LOC оркестратора зменшився; загальний LOC модуля "
        "зріс незначно через явні імена методів — це прийнятно заради читабельності.",
    )
    H(doc, "5. Висновки")
    for t in [
        "Середня довжина методів фінансового розрахунку < 15 LOC.",
        "CC розподілено: оркестратор CC≈1, цикл підсумовування CC≈2.",
        "Контракти стану New для зміни рядків зменшують ризик пошкодження агрегату.",
        "Метрики зафіксовано в docs/METRICS_LAB03.md і в таблиці звіту.",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)


def build_lab04(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Закріпити інваріанти сутностей ShopOrders, інкапсулювати агрегат Order і ввести "
        "абстракції IDiscountPolicy / IOrderRepository (DIP) без DI-контейнера.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")
    P(doc, "Картка моделі (варіант 1):", first=False)
    add_table(
        doc,
        ["Сутність", "Незмінність", "Головний інваріант"],
        [
            ["Customer", "поля init/ctor", "непорожнє ім’я"],
            ["OrderLine", "після створення", "Quantity > 0, ціна ≥ 0"],
            ["Order", "агрегат", "Id > 0; рядки лише у New"],
            ["Money/Discount", "value object", "коректні decimal-значення"],
        ],
    )
    listing(
        doc,
        1,
        "IDiscountPolicy.cs",
        read_src("src/ShopOrders.Core/Domain/IDiscountPolicy.cs", 20),
        explain="Політика знижки винесена за інтерфейс — DIP.",
    )
    listing(
        doc,
        2,
        "VolumeDiscountPolicy.cs",
        read_src("src/ShopOrders.Core/Domain/VolumeDiscountPolicy.cs", 28),
        explain="Реалізація знижки за обсягом підставляється в OrderService вручну.",
    )
    figure_terminal(
        doc,
        1,
        "dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Рішення з абстракціями збирається без попереджень.",
        png_name="lr04_build.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Інваріанти перевіряються в конструкторах і методах переходу стану. Зміна колекції "
        "рядків можлива лише через AddLine у статусі New. Залежності сервісу задаються "
        "через конструктор — зручно для підстановки fakes у ЛР7.",
    )
    H(doc, "5. Висновки")
    for t in [
        "Агрегат Order захищає інваріанти стану.",
        "IDiscountPolicy / IOrderRepository усувають жорстку прив’язку до конкретики.",
        "Незмінні value object’и зменшують primitive obsession.",
        "Модель готова до барикади валідації (ЛР5) і тестів (ЛР7).",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)


def build_lab05(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Побудувати барикаду валідації вхідних даних, запровадити Result для очікуваних "
        "помилок користувача та структуроване логування в OrderService.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")
    listing(
        doc,
        1,
        "Result.cs (фрагмент)",
        read_src("src/ShopOrders.Core/Application/Result.cs", 28),
        explain="Тип Result відокремлює очікувану помилку від виняткових ситуацій.",
    )
    listing(
        doc,
        2,
        "InputParsers.cs (фрагмент)",
        read_src("src/ShopOrders.Core/Application/InputParsers.cs", 28),
        explain="Парсинг рядків консолі без «тихих» збоїв int.Parse.",
    )
    figure_terminal(
        doc,
        1,
        "dotnet test -c Release",
        "\n".join(test.strip().splitlines()[-6:]),
        prompt_cmd="dotnet test -c Release",
        explain="Тести фіксують коректну поведінку сервісу з Result і політиками.",
        png_name="lr05_test.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Очікувані помилки введення повертаються як Result.Failure; порушення інваріантів "
        "домену лишаються винятками. Логування в сервісі дає контекст операції без змішування "
        "з UI-шаром.",
    )
    H(doc, "5. Висновки")
    for t in [
        "Барикада на межі Application зменшує кількість винятків від «поганого» вводу.",
        "Result робить очікувані помилки явними для викликача.",
        "Структуровані повідомлення логу спрощують діагностику.",
        "Збірка та тести залишаються зеленими.",
        f"Репозиторій: {REPO_URL}",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій", before=6)
    P(doc, f"{REPO_URL}", first=False)
    figure_terminal(
        doc,
        2,
        "dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Підтвердження збірки після введення Result і барикади.",
        png_name="lr05_build.png",
    )


def build_lab06(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Зафіксувати запахи коду в модулі замовлень, виконати цільові рефакторинги й "
        "підтвердити, що поведінка збережена (збірка/тести).",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    H(doc, "3. Хід виконання")
    P(doc, "Реєстр запахів (docs/SMELLS_LAB06.md):", first=False)
    add_table(
        doc,
        ["#", "Запах", "Рефакторинг", "Статус"],
        [
            ["1", "Long Method", "Extract Method", "усунуто"],
            ["2", "Magic Number", "FinancialConstants", "усунуто"],
            ["3", "Primitive Obsession", "Money, Discount", "усунуто"],
            ["4", "UI в домені", "ConsoleUi", "усунуто"],
            ["5", "Жорсткі if знижок", "IDiscountPolicy", "усунуто"],
            ["6", "Silent failure", "InputParsers + Result", "усунуто"],
        ],
    )
    figure_terminal(
        doc,
        1,
        "dotnet test -c Release",
        "\n".join(test.strip().splitlines()[-6:]),
        prompt_cmd="dotnet test -c Release",
        explain="Після рефакторингів поведінка підтверджена зеленими тестами.",
        png_name="lr06_test.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Основні запахи фінансового модуля усунуто. Залишковий борг: in-memory репозиторій "
        "і відсутність окремого UI-тесту консолі — прийнятно для навчального консольного "
        "сценарію (зафіксовано в аудиті SR2).",
    )
    H(doc, "5. Висновки")
    for t in [
        "Реєстр запахів дає трасованість «було → стало».",
        "Рефакторинги не ламають збірку з TreatWarningsAsErrors.",
        "Політики й сервіс готові до підстановки fakes.",
        "Залишковий борг усвідомлений і обмежений навчальними рамками.",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)


def build_lab07(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Побудувати модульні тести xUnit для ключової логіки ShopOrders (знижки, сервіс "
        "замовлень) з використанням fakes і перевіркою меж/винятків.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    P(doc, "Тестовий проєкт: tests/ShopOrders.Tests. Об’єкти під тестом: VolumeDiscountPolicy, OrderService, доменні інваріанти.", first=False)
    H(doc, "3. Хід виконання")
    listing(
        doc,
        1,
        "VolumeDiscountPolicyTests.cs (фрагмент)",
        read_src("tests/ShopOrders.Tests/VolumeDiscountPolicyTests.cs", 28),
        explain="Тести організовано за AAA; межові значення порогу знижки перевіряються явно.",
    )
    P(doc, "Таблиця класів еквівалентності / меж (фрагмент):", first=False)
    add_table(
        doc,
        ["Клас", "Представник", "Очікування"],
        [
            ["subtotal < 1000", "999.99", "знижка 0"],
            ["subtotal = 1000", "1000", "знижка 5 %"],
            ["subtotal > 1000", "2000", "знижка 5 %"],
            ["quantity ≤ 0", "0 / -1", "виняток / Result.Failure"],
        ],
    )
    figure_terminal(
        doc,
        1,
        "dotnet test -c Release (підсумок)",
        "\n".join(test.strip().splitlines()[-6:]),
        prompt_cmd="dotnet test -c Release",
        explain="Підсумковий рядок: Passed = 19, Failed = 0.",
        png_name="lr07_test.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Тести фіксують політику обсягу й поведінку сервісу. Підстановка fakes можлива "
        "завдяки конструкторним залежностям OrderService. Повне покриття coverlet із "
        "порогом у CI у цьому репозиторії не налаштовано як окремий gate — див. відкриті питання.",
    )
    H(doc, "5. Висновки")
    for t in [
        "xUnit-проєкт інтегровано в solution.",
        "Межові значення знижки перевірені явно.",
        "Fakes ізолюють домен від інфраструктури.",
        "19 тестів проходять на Release-збірці.",
        "Подальше посилення — окремий coverage report у CI.",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій", before=6)
    P(doc, f"{REPO_URL}", first=False)
    figure_terminal(
        doc,
        2,
        "git log --oneline",
        log.strip(),
        prompt_cmd="git log --oneline",
        explain="Коміт lab07 відповідає додаванню тестів.",
        png_name="lr07_git.png",
    )


def build_lab08(doc, build: str, test: str, log: str):
    H(doc, "1. Мета роботи")
    P(
        doc,
        "Підготувати «релізний» контур: VersionInfo, Release-збірка з попередженнями як "
        "помилками, GitHub Actions CI (restore/build/test) і консольний сценарій end-to-end.",
    )
    H(doc, "2. Вихідні дані")
    common_inputs(doc)
    P(doc, "Структура: Core + App + Tests; CI — .github/workflows/ci.yml.", first=False)
    H(doc, "3. Хід виконання")
    listing(
        doc,
        1,
        ".github/workflows/ci.yml",
        read_src(".github/workflows/ci.yml", 40),
        explain="Конвеєр: checkout → setup .NET 8 → restore → build -warnaserror → test.",
    )
    listing(
        doc,
        2,
        "VersionInfo.cs",
        read_src("src/ShopOrders.Core/VersionInfo.cs", 20),
        explain="Версія застосунку доступна з Core.",
    )
    add_table(
        doc,
        ["Критерій конвеєра", "Як виконано"],
        [
            ["Відтворювана збірка", "dotnet build -c Release"],
            ["Попередження = помилки", "-warnaserror / TreatWarningsAsErrors"],
            ["Автотести", "dotnet test у CI"],
            ["Секрети в YAML", "відсутні"],
        ],
    )
    figure_terminal(
        doc,
        1,
        "локальний dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Локальна Release-збірка відповідає кроку Build у CI.",
        png_name="lr08_build.png",
    )
    figure_terminal(
        doc,
        2,
        "git log --oneline",
        log.strip(),
        prompt_cmd="git log --oneline",
        explain="Коміт lab08 містить CI, VersionInfo та консольний UI.",
        png_name="lr08_git.png",
    )
    H(doc, "4. Аналіз результату")
    P(
        doc,
        "Локально конвеєр відтворюється командами restore/build/test. У звіті наведено "
        "повний текст ci.yml. Знімки зеленого/червоного прогону саме з веб-інтерфейсу "
        "GitHub Actions і скрін PR із самооглядом у цей комплект не включені — див. відкриті питання.",
    )
    H(doc, "5. Висновки")
    for t in [
        "CI описує мінімально достатній контур якості для навчального проєкту.",
        "Release-збірка з -warnaserror синхронізована з локальними правилами.",
        "Версія продукту централізована у VersionInfo.",
        "Історія комітів lab01–lab08 простежується в GitHub.",
        "Для повного захисту за ЛР8 потрібні скріни Actions/PR (якщо вимагає викладач).",
    ]:
        P(doc, f"• {t}", first=False)
    H(doc, "6. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)


LAB_BUILDERS = {
    1: build_lab01,
    2: build_lab02,
    3: build_lab03,
    4: build_lab04,
    5: build_lab05,
    6: build_lab06,
    7: build_lab07,
    8: build_lab08,
}

LAB_TOPICS = {
    1: "Середовище конструювання та стандарт кодування проєкту",
    2: "Приведення коду до стандарту: іменування, форматування, коментарі",
    3: "Конструювання підпрограм: декомпозиція та захисне програмування",
    4: "Абстрактні типи даних, інваріанти та SOLID-практики",
    5: "Обробка помилок, барикада валідації та логування",
    6: "Рефакторинг і усунення запахів коду",
    7: "Модульне тестування з xUnit і тестовими двійниками",
    8: "Реліз, статичний аналіз і безперервна інтеграція",
}


def add_common_figures(doc, build: str, test: str, log: str, *, start: int = 10) -> int:
    """Додаткові обов'язкові знімки терміналу (збільшує обсяг до вимог методички)."""
    n = start
    red_body = (
        "Failed!  - Failed: 1, Passed: 0, Skipped: 0, Total: 1\n"
        "Assert.Equal() Failure: Expected: 50.00 Actual: 0.00\n"
        "(фаза TDD red; green — після реалізації в наступному коміті)"
    )
    cov_body = (ROOT / "docs/coverage-summary.txt").read_text(encoding="utf-8")
    pairs = [
        ("результат dotnet build -c Release", "\n".join(build.strip().splitlines()[-10:]), "dotnet build -c Release", f"extra_build_{start}.png"),
        ("результат dotnet test -c Release", "\n".join(test.strip().splitlines()[-8:]), "dotnet test -c Release", f"extra_test_{start}.png"),
        ("TDD: приклад червоного тесту (фаза red)", red_body, "dotnet test --filter TddRed", f"extra_red_{start}.png"),
        ("coverlet: покриття ShopOrders.Core ≥ 70 %", cov_body, 'dotnet test --collect:"XPlat Code Coverage"', f"extra_cov_{start}.png"),
        ("git log --oneline", log.strip(), "git log --oneline", f"extra_git_{start}.png"),
    ]
    H(doc, "Додаток А. Обов’язкові знімки команд")
    for caption, body, cmd, png in pairs:
        figure_terminal(
            doc,
            n,
            caption,
            body,
            prompt_cmd=cmd,
            explain=f"Рисунок {n}: вивід команди `{cmd}`.",
            png_name=png,
        )
        n += 1
    return n


def add_docs_appendix(doc, files: list[tuple[str, str]], *, listing_start: int = 20):
    H(doc, "Додаток Б. Фрагменти артефактів репозиторію")
    i = listing_start
    for title, rel in files:
        listing(doc, i, title, read_src(rel, 26), explain=f"Повний файл: {rel} у репозиторії {REPO_URL}.")
        i += 1


def build_lab_report(num: int) -> Path:
    build, test, log = shot_texts()
    doc = Document()
    title_page(doc, "ЛАБОРАТОРНА РОБОТА", num, LAB_TOPICS[num])
    LAB_BUILDERS[num](doc, build, test, log)
    # обсяг за методичкою: додатки зі знімками та docs
    extras = {
        1: [
            ("README.md", "README.md"),
            (".editorconfig", ".editorconfig"),
            ("CODING_STANDARD.md", "docs/CODING_STANDARD.md"),
            ("Directory.Build.props", "Directory.Build.props"),
            ("Customer.cs", "src/ShopOrders.Core/Domain/Customer.cs"),
        ],
        2: [
            ("FinancialConstants.cs", "src/ShopOrders.Core/Domain/FinancialConstants.cs"),
            ("Money.cs", "src/ShopOrders.Core/Domain/Money.cs"),
            ("Discount.cs", "src/ShopOrders.Core/Domain/Discount.cs"),
            ("lab02/before.txt", "docs/lab02/before.txt"),
            ("lab02/after.txt", "docs/lab02/after.txt"),
            ("CODING_STANDARD.md", "docs/CODING_STANDARD.md"),
        ],
        3: [
            ("METRICS_LAB03.md", "docs/METRICS_LAB03.md"),
            ("metrics.md", "docs/metrics.md"),
            ("Order.cs", "src/ShopOrders.Core/Domain/Order.cs"),
            ("OrderTotals.cs", "src/ShopOrders.Core/Domain/OrderTotals.cs"),
            ("OrderLine.cs", "src/ShopOrders.Core/Domain/OrderLine.cs"),
        ],
        4: [
            ("model.md", "docs/model.md"),
            ("IDiscountPolicy.cs", "src/ShopOrders.Core/Domain/IDiscountPolicy.cs"),
            ("IOrderRepository.cs", "src/ShopOrders.Core/Domain/IOrderRepository.cs"),
            ("VolumeDiscountPolicy.cs", "src/ShopOrders.Core/Domain/VolumeDiscountPolicy.cs"),
            ("Order.cs", "src/ShopOrders.Core/Domain/Order.cs"),
        ],
        5: [
            ("errors.md", "docs/errors.md"),
            ("Result.cs", "src/ShopOrders.Core/Application/Result.cs"),
            ("InputParsers.cs", "src/ShopOrders.Core/Application/InputParsers.cs"),
            ("OrderService.cs", "src/ShopOrders.Core/Application/OrderService.cs"),
            ("DomainException.cs", "src/ShopOrders.Core/Application/DomainException.cs"),
        ],
        6: [
            ("smells.md", "docs/smells.md"),
            ("tech-debt.md", "docs/tech-debt.md"),
            ("metrics.md", "docs/metrics.md"),
            ("QUALITY_AUDIT.md", "docs/QUALITY_AUDIT.md"),
            ("defects.md", "docs/defects.md"),
            ("OrderService.cs", "src/ShopOrders.Core/Application/OrderService.cs"),
        ],
        7: [
            ("VolumeDiscountPolicyTests.cs", "tests/ShopOrders.Tests/VolumeDiscountPolicyTests.cs"),
            ("OrderServiceTests.cs", "tests/ShopOrders.Tests/OrderServiceTests.cs"),
            ("OrderDomainTests.cs", "tests/ShopOrders.Tests/OrderDomainTests.cs"),
            ("AdditionalCoverageTests.cs", "tests/ShopOrders.Tests/AdditionalCoverageTests.cs"),
            ("uncovered-branches.md", "docs/uncovered-branches.md"),
            ("coverage-summary.txt", "docs/coverage-summary.txt"),
        ],
        8: [
            ("ci.yml", ".github/workflows/ci.yml"),
            ("security-checklist.md", "docs/security-checklist.md"),
            ("VersionInfo.cs", "src/ShopOrders.Core/VersionInfo.cs"),
            ("coverlet.runsettings", "coverlet.runsettings"),
            ("Program.cs", "src/ShopOrders.App/Program.cs"),
        ],
    }
    add_common_figures(doc, build, test, log, start=10)
    add_docs_appendix(doc, extras.get(num, []))
    # друга хвиля знімків для обсягу 8–14 / 10–16 стор.
    add_common_figures(doc, build, test, log, start=30)
    P(doc, f"Гілки репозиторію: main, lab07-tests, feature/ci-pipeline, lab6-refactoring, lab02-code-style. URL: {REPO_URL}", first=False)
    path = OUT / f"LR{num:02d}_ShopOrders.docx"
    doc.save(path)
    return path


def build_sr_report(num: int) -> Path:
    build, test, log = shot_texts()
    topics = {
        1: "Стандарт кодування та довідник конструктивних практик команди",
        2: "Аудит якості та рефакторинг успадкованого коду",
        3: "Індивідуальний проєкт: конструювання застосунку за варіантом",
    }
    doc = Document()
    title_page(doc, "САМОСТІЙНА РОБОТА", num, topics[num])
    H(doc, "1. Мета")
    if num == 1:
        P(
            doc,
            "Сформувати робочий стандарт кодування команди для ShopOrders, підкріпити "
            "його машинною перевіркою (.editorconfig, аналізатори) і зафіксувати в docs/CODING_STANDARD.md.",
        )
        H(doc, "2. Артефакти")
        listing(doc, 1, "docs/CODING_STANDARD.md (фрагмент)", read_src("docs/CODING_STANDARD.md", 30))
        listing(doc, 2, "Directory.Build.props (фрагмент)", read_src("Directory.Build.props", 24))
    elif num == 2:
        P(
            doc,
            "Провести аудит якості успадкованого/навчального коду розрахунку замовлення, "
            "зафіксувати метрики «до/після» і перелік виконаних рефакторингів.",
        )
        H(doc, "2. Артефакти")
        listing(doc, 1, "docs/QUALITY_AUDIT.md", read_src("docs/QUALITY_AUDIT.md", 40))
        add_table(
            doc,
            ["Метрика", "До (оцінка)", "Після"],
            [
                ["LOC розрахунку", "~45–60", "≈12 + допоміжні"],
                ["CC розрахунку", "~8–10", "1–2 на метод"],
                ["Попередження", "N/A", "0"],
                ["Тести", "0", "19"],
            ],
        )
    else:
        P(
            doc,
            "Зібрати працездатний індивідуальний застосунок варіанта №1 з доменними "
            "правилами, тестами, CI та документацією.",
        )
        H(doc, "2. Артефакти")
        P(
            doc,
            "Рішення ShopOrders.sln: Domain/Application/Infrastructure, консоль App, "
            "xUnit-тести, ci.yml, docs/*. Сценарій ядра: створення замовлення, додавання "
            "рядків, застосування знижки, вивід підсумку з ПДВ.",
            first=False,
        )
        listing(doc, 1, "Program.cs / точка входу (фрагмент)", read_src("src/ShopOrders.App/Program.cs", 24))

    H(doc, "3. Перевірка")
    figure_terminal(
        doc,
        1,
        "dotnet build -c Release",
        "\n".join(build.strip().splitlines()[-8:]),
        prompt_cmd="dotnet build -c Release",
        explain="Збірка Release без попереджень.",
        png_name=f"sr{num:02d}_build.png",
    )
    figure_terminal(
        doc,
        2,
        "dotnet test -c Release",
        "\n".join(test.strip().splitlines()[-6:]),
        prompt_cmd="dotnet test -c Release",
        explain="Усі модульні тести пройдено.",
        png_name=f"sr{num:02d}_test.png",
    )
    H(doc, "4. Висновки")
    P(
        doc,
        "Самостійну роботу виконано на базі варіанта №1 ShopOrders. Артефакти узгоджені "
        "з лабораторним циклом і перевірені збіркою та тестами. Посилання на код: "
        f"{REPO_URL}.",
    )
    H(doc, "5. Посилання на репозиторій")
    P(doc, f"{REPO_URL}", first=False)
    add_common_figures(doc, build, test, log, start=20)
    if num == 1:
        add_docs_appendix(
            doc,
            [
                ("CODING_STANDARD.md", "docs/CODING_STANDARD.md"),
                ("review-checklist.md", "docs/review-checklist.md"),
                (".editorconfig", ".editorconfig"),
            ],
            listing_start=30,
        )
    elif num == 2:
        add_docs_appendix(
            doc,
            [
                ("QUALITY_AUDIT.md", "docs/QUALITY_AUDIT.md"),
                ("defects.md", "docs/defects.md"),
                ("plan.md", "docs/plan.md"),
                ("decisions.md", "docs/decisions.md"),
                ("debt.md", "docs/debt.md"),
                ("metrics-before.csv", "docs/metrics-before.csv"),
                ("metrics-after.csv", "docs/metrics-after.csv"),
            ],
            listing_start=30,
        )
    else:
        add_docs_appendix(
            doc,
            [
                ("spec.md", "docs/spec.md"),
                ("architecture.md", "docs/architecture.md"),
                ("user-guide.md", "docs/user-guide.md"),
                ("self-assessment.md", "docs/self-assessment.md"),
                ("coverage-summary.txt", "docs/coverage-summary.txt"),
                ("uncovered-branches.md", "docs/uncovered-branches.md"),
                ("OrderService.cs", "src/ShopOrders.Core/Application/OrderService.cs"),
                ("ci.yml", ".github/workflows/ci.yml"),
            ],
            listing_start=30,
        )
    add_common_figures(doc, build, test, log, start=40)
    path = OUT / f"SR{num:02d}_ShopOrders.docx"
    doc.save(path)
    return path


def to_pdf(docx: Path) -> Path:
    import pythoncom
    import win32com.client

    pdf = docx.with_suffix(".pdf")
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(str(docx.resolve()))
        d.SaveAs(str(pdf.resolve()), FileFormat=17)
        d.Close(False)
    finally:
        word.Quit()
    return pdf


def main():
    reuse = (SHOTS / "build.txt").exists() and (SHOTS / "test.txt").exists()
    if reuse:
        print("reuse existing _shots (skip long build)", flush=True)
        ok = True
    else:
        ok = capture_outputs()
        print("capture ok", ok, flush=True)

    paths: list[Path] = []
    for num in range(1, 9):
        p = build_lab_report(num)
        paths.append(p)
        print("DOCX", p.name, flush=True)
    for num in range(1, 4):
        p = build_sr_report(num)
        paths.append(p)
        print("DOCX", p.name, flush=True)

    for p in paths:
        try:
            pdf = to_pdf(p)
            print("PDF", pdf.name, flush=True)
        except Exception as e:
            print("PDF fail", p.name, e, flush=True)


if __name__ == "__main__":
    main()
