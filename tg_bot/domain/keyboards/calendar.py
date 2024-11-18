import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_calendar(
    year: int = datetime.now(tz=None).year, month: int = datetime.now(tz=None).month
):
    builder = InlineKeyboardBuilder()
    keyboard = []
    # Заголовок с месяцем и годом
    row = []
    row.append(
        InlineKeyboardButton(
            text=f"{calendar.month_name[month]} {year}", callback_data="ignore"
        )
    )
    builder.row(*row)
    # Дни недели
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(text=day, callback_data="ignore"))
    builder.row(*row)
    # Дни месяца
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day), callback_data=f"set_date:{year}:{month}:{day}"
                    )
                )
        builder.row(*row)
    # Кнопки навигации
    row = []
    prev_month = datetime(year, month, 1) - timedelta(days=1)
    next_month = datetime(year, month, 28) + timedelta(
        days=4
    )  # Переходим к следующему месяцу
    row.append(
        InlineKeyboardButton(
            text="⏪", callback_data=f"prev_month:{prev_month.year}:{prev_month.month}"
        )
    )
    row.append(
        InlineKeyboardButton(
            text="⏩", callback_data=f"next_month:{next_month.year}:{next_month.month}"
        )
    )
    builder.row(*row)
    return builder.as_markup()
