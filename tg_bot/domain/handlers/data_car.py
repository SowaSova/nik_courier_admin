from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
)

from apps.users.models import TelegramUser
from tg_bot.domain.keyboards.calendar import create_calendar
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.bot_config import create_reply_markup, get_bot_message

router = Router()


@router.callback_query(ApplicationForm.WaitingForCarTonnage)
async def process_car_tonnage(
    callback_query: CallbackQuery,
    state: FSMContext,
    user: TelegramUser,
):
    data = await state.get_data()
    car_tonnage = callback_query.data
    await state.update_data(car_tonnage=car_tonnage)

    if data.get("referral"):
        # Fetch message and buttons from database
        bot_message_text, media, buttons = await get_bot_message(
            "choose_document_provision_method"
        )

        if not bot_message_text:
            bot_message_text = "Выберите способ предоставления документов:"

        reply_markup = create_reply_markup(buttons)

        await callback_query.message.edit_text(
            bot_message_text, reply_markup=reply_markup
        )
        await state.set_state(ApplicationForm.WaitingForDocumentChoice)
        await callback_query.answer()
    else:
        # Fetch message from database
        bot_message_text, _, _ = await get_bot_message("select_date_for_documents")
        if not bot_message_text:
            bot_message_text = "Выберите дату для предоставления документов:"

        calendar_markup = create_calendar()

        await callback_query.message.edit_text(
            bot_message_text, reply_markup=calendar_markup
        )
        await state.set_state(ApplicationForm.WaitingForAppointmentDate)
        await callback_query.answer()
