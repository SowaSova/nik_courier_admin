from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from adminpanel.constants import ApplicationStatus
from tg_bot.domain.callbacks import ApplicationStatusCallback


def send_status_choice_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=ApplicationStatus.NEW.label,
            callback_data=ApplicationStatusCallback(
                status=ApplicationStatus.NEW.value
            ).pack(),
        ),
        InlineKeyboardButton(
            text=ApplicationStatus.ACTIVE.label,
            callback_data=ApplicationStatusCallback(
                status=ApplicationStatus.ACTIVE.value
            ).pack(),
        ),
        InlineKeyboardButton(
            text=ApplicationStatus.CLOSED.label,
            callback_data=ApplicationStatusCallback(
                status=ApplicationStatus.CLOSED.value
            ).pack(),
        ),
    )
    builder.adjust(1)
    return builder.as_markup()
