from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tg_bot.domain.states import ApplicationForm

router = Router()


@router.callback_query(ApplicationForm.WaitingForVacancyChoice)
async def process_vacancy_choice(callback_query: CallbackQuery, state: FSMContext):
    vacancy_id = callback_query.data.split(":")[-1]
    await state.update_data(vacancy_id=vacancy_id)
    await callback_query.message.edit_text("Пожалуйста, введите полностью Ваше ФИО:")
    await state.set_state(ApplicationForm.WaitingForFullName)
    await callback_query.answer()
