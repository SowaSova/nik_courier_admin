from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def send_partner_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="👤 Личный кабинет",
            callback_data="personal_cabinet",
        ),
        InlineKeyboardButton(
            text="📩 Разместить заявку",
            callback_data="start_application",
        ),
        InlineKeyboardButton(
            text="🔗 Реферальные ссылки",
            callback_data="referral_links",
        ),
        InlineKeyboardButton(
            text="🏫 Обучение",
            callback_data="training",
        ),
    )
    builder.adjust(2)
    return builder.as_markup()
