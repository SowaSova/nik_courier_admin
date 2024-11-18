from typing import List, Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.models import BotButton, BotMedia
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.bot_config import (
    create_reply_markup,
    get_bot_message,
    send_bot_message,
    with_bot_message,
)
from users.models import TelegramUser

router = Router()


@router.message(ApplicationForm.WaitingForFullName)
@with_bot_message("enter_phone_number")
async def process_full_name(
    message: Message,
    state: FSMContext,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)

    if not bot_message_text:
        bot_message_text = "Пожалуйста, введите ваш номер телефона:"

    reply_markup = create_reply_markup(buttons)

    await send_bot_message(message, bot_message_text, media, reply_markup, user)
    await state.set_state(ApplicationForm.WaitingForPhoneNumber)
