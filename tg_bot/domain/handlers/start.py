from typing import List, Optional

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from apps.bot.models import BotButton, BotMedia
from apps.users.models import TelegramUser
from tg_bot.domain.keyboards.city_choice import send_cities_keyboard
from tg_bot.domain.states.application import ApplicationForm
from tg_bot.utils import application_exists, with_bot_message
from tg_bot.utils.bot_config import (
    create_reply_markup,
    get_bot_message,
    send_bot_message,
)

router = Router()


@router.message(CommandStart())
@with_bot_message("start_message_partner")
async def process_start_command(
    message: Message,
    state: FSMContext,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    if user.is_partner:
        if not bot_message_text:
            bot_message_text = "Добро пожаловать, {name}!"
        reply_markup = create_reply_markup(buttons)
        await send_bot_message(message, bot_message_text, media, reply_markup, user)
    else:
        (
            bot_message_text_courier,
            media_courier,
            buttons_courier,
        ) = await get_bot_message("start_message_courier")
        if not bot_message_text_courier:
            bot_message_text_courier = "Добро пожаловать, {name}! Выберите свой город:"
        if not await application_exists(user):
            await state.update_data(referral=True)
            cities_kb = await send_cities_keyboard()
            no_cities_msg, _, _ = await get_bot_message("cities_not_found")
            if not cities_kb:
                await message.answer(no_cities_msg or "Нет доступных городов")
            else:
                await send_bot_message(
                    message,
                    bot_message_text_courier,
                    media_courier,
                    cities_kb,
                    user,
                )
                await state.set_state(ApplicationForm.WaitingForCityChoice)
        else:
            apply_already, _, _ = await get_bot_message("apply_already_exists")
            await message.answer(apply_already or "Заявка уже существует")
