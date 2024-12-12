from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_button_or_builder(entity: str, builder: bool = False):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="↩️ Назад", callback_data=f"back_to_{entity}"))
    return kb.as_markup() if not builder else kb


# def get_back_button_builder(entity: str):
#     builder = InlineKeyboardBuilder()
#     builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data=f"back_to_{entity}"))
#     return builder
