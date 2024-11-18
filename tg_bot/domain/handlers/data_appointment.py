from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from adminpanel.constants import CarTonnage
from tg_bot.domain.states import ApplicationForm
from users.models import TelegramUser

router = Router()


@router.message(ApplicationForm.WaitingForAppointmentDate)
async def process_appointment_date(
    message: Message, state: FSMContext, user: TelegramUser
):
    appointment_date = message.text.strip()
    await state.update_data(appointment_date=appointment_date)
    await message.edit_text(f"Спасибо, вы назначили дату: {appointment_date}")
