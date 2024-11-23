from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from apps.users.models import TelegramUser
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.bot_config import get_bot_message

router = Router()


@router.message(ApplicationForm.WaitingForAppointmentDate)
async def process_appointment_date(
    message: Message, state: FSMContext, user: TelegramUser
):
    appointment_date = message.text.strip()
    msg = await get_bot_message("appointment_date_success")
    if not msg:
        msg = "Вы назначили дату: {appointment_date}"
    msg = msg.format(appointment_date=appointment_date)
    await state.update_data(appointment_date=appointment_date)
    await message.edit_text(msg)
