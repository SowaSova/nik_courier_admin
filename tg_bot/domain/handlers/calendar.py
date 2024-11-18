from datetime import datetime

from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tg_bot.domain.keyboards import create_calendar
from tg_bot.domain.states.application import ApplicationForm
from tg_bot.domain.states.personal_cabinet import PersonalCabinetForm
from tg_bot.utils import finalize_application
from tg_bot.utils.bot_config import get_bot_message
from users.models import TelegramUser

router = Router()


@router.callback_query(F.data.startswith("set_date"))
async def process_set_date(
    callback_query: CallbackQuery,
    state: FSMContext,
    user: TelegramUser,
):
    cur_state = await state.get_state()
    _, year, month, day = callback_query.data.split(":")
    selected_date = datetime(int(year), int(month), int(day))
    if selected_date < datetime.now(tz=None):
        bot_message_text, _, _ = await get_bot_message("error_past_date_selected")
        if not bot_message_text:
            bot_message_text = (
                "Вы выбрали прошедшую дату. Пожалуйста, выберите дату в будущем."
            )

        await callback_query.message.answer(bot_message_text)
        return
    await state.update_data(appointment_date=selected_date)
    if cur_state and cur_state.startswith(ApplicationForm.__name__):
        bot_message_text, _, _ = await get_bot_message("date_selected_confirmation")
        if not bot_message_text:
            bot_message_text = (
                "Вы выбрали дату: {selected_date}\nЗаявка принята в обработку."
            )

        message_text = bot_message_text.format(
            selected_date=selected_date.strftime("%d.%m.%Y")
        )

        await callback_query.message.edit_text(message_text)
        await finalize_application(state, callback_query.message, user)
    elif cur_state and cur_state.startswith(PersonalCabinetForm.__name__):
        from tg_bot.utils import get_applies

        applications = await get_applies(user, state)
        if not applications:
            bot_message_text, _, _ = await get_bot_message("no_applications_found")
            if not bot_message_text:
                bot_message_text = "Нет заявок на выбранную дату"

            await callback_query.answer(bot_message_text, show_alert=True)
            return

        bot_message_text, _, _ = await get_bot_message("applications_list")
        if not bot_message_text:
            bot_message_text = "Ваши заявки:\n{applications}"

        applications_text = ""
        for application in applications:
            applications_text += (
                f"- {application.full_name}\n- {application.phone_number}\n\n"
            )

        message_text = bot_message_text.format(applications=applications_text)

        await callback_query.message.edit_text(message_text)
        await callback_query.answer()
    else:
        await callback_query.answer(
            await get_bot_message("unknown_state") or "Неизвестное состояние",
            show_alert=True,
        )
        return


@router.callback_query(F.data.startswith("prev_month"))
async def process_prev_month(callback_query: CallbackQuery):
    _, year, month = callback_query.data.split(":")
    calendar_markup = create_calendar(int(year), int(month))
    await callback_query.message.edit_reply_markup(reply_markup=calendar_markup)
    await callback_query.answer()


@router.callback_query(F.data.startswith("next_month"))
async def process_next_month(callback_query: CallbackQuery):
    _, year, month = callback_query.data.split(":")
    calendar_markup = create_calendar(int(year), int(month))
    await callback_query.message.edit_reply_markup(reply_markup=calendar_markup)
    await callback_query.answer()
