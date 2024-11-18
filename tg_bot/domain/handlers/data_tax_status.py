from typing import List, Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from adminpanel.constants import CarTonnage
from bot.models import BotButton, BotMedia
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.bot_config import create_reply_markup, with_bot_message
from users.models import TelegramUser

router = Router()


@router.callback_query(ApplicationForm.WaitingForTaxStatus)
@with_bot_message("choose_car_tonnage")
async def process_tax_status(
    callback_query: CallbackQuery,
    state: FSMContext,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    tax_status = callback_query.data
    await state.update_data(tax_status=tax_status)

    if not bot_message_text:
        bot_message_text = "Выберите грузоподъемность вашего автомобиля:"

    reply_markup = create_reply_markup(buttons)

    await callback_query.message.edit_text(bot_message_text, reply_markup=reply_markup)
    await state.set_state(ApplicationForm.WaitingForCarTonnage)
    await callback_query.answer()
