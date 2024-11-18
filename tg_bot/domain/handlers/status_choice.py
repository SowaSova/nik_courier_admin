from aiogram import F, Router
from aiogram.types import CallbackQuery

from tg_bot.domain.callbacks import ApplicationStatusCallback
from tg_bot.domain.keyboards import send_cities_keyboard
from tg_bot.domain.states import PersonalCabinetForm

router = Router()


@router.callback_query(ApplicationStatusCallback.filter())
async def process_status_choice(
    callback_query: CallbackQuery, state: PersonalCabinetForm
):
    status = callback_query.data
    await state.update_data(status=status)
    await callback_query.message.edit_text(
        "Выберите город:", reply_markup=await send_cities_keyboard()
    )
    await state.set_state(PersonalCabinetForm.WaitingForCityChoice)
    await callback_query.answer()
