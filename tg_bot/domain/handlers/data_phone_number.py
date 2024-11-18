from typing import List, Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from adminpanel.constants import TaxStatus
from bot.models import BotButton, BotMedia
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils import schedule_timeout_check
from tg_bot.utils.bot_config import (
    create_reply_markup,
    send_bot_message,
    with_bot_message,
)
from users.models import TelegramUser

router = Router()


@router.message(ApplicationForm.WaitingForPhoneNumber)
@with_bot_message("choose_tax_status")
async def process_phone_number(
    message: Message,
    state: FSMContext,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    phone_number = message.text.strip()
    await state.update_data(phone_number=phone_number)

    if not bot_message_text:
        bot_message_text = "Выберите ваш налоговый статус:"

    reply_markup = create_reply_markup(buttons)

    await send_bot_message(message, bot_message_text, media, reply_markup, user)
    await state.set_state(ApplicationForm.WaitingForTaxStatus)
