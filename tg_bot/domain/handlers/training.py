from typing import List, Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from apps.bot.models import BotButton, BotMedia
from tg_bot.domain.keyboards.city_choice import send_cities_keyboard
from tg_bot.domain.states import TrainingCandidateForm
from tg_bot.utils.bot_config import (
    create_reply_markup,
    get_bot_message,
    with_bot_message,
)

router = Router()


@router.callback_query(F.data == "training")
@with_bot_message("training")
async def training_menu(
    callback_query: CallbackQuery,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    if not bot_message_text:
        bot_message_text = "Выберите запрашиваемую информацию:"

    reply_markup = create_reply_markup(buttons)

    await callback_query.message.answer(bot_message_text, reply_markup=reply_markup)


@router.callback_query(F.data == "company_info")
@with_bot_message("company_info")
async def training_menu(
    callback_query: CallbackQuery,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    if not bot_message_text:
        bot_message_text = "Информация о компании есть"
    if media:
        file = FSInputFile(media.file.path)
        await callback_query.message.answer_photo(photo=file, caption=bot_message_text)
    else:
        await callback_query.message.answer(bot_message_text)


@router.callback_query(F.data == "application_info")
async def training_menu(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    bot_message, _, _ = await get_bot_message("city_choice")
    if not bot_message:
        bot_message = "Выберите город:"
    await callback_query.message.answer(
        text=str(bot_message), reply_markup=await send_cities_keyboard()
    )
    await state.set_state(TrainingCandidateForm.WaitingForCityChoice)
    await callback_query.answer()
