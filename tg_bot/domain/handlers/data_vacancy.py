from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from apps.geo.models import City
from apps.users.models import Partner, TelegramUser
from tg_bot.domain.callbacks import VacancyCallback
from tg_bot.domain.states import ApplicationForm
from tg_bot.domain.states.candidate_info import TrainingCandidateForm
from tg_bot.utils.applies_get import get_applies_by_vacancy, get_vacancy
from tg_bot.utils.bot_config import get_bot_message

router = Router()


@router.callback_query(VacancyCallback.filter())
async def process_vacancy_choice(
    callback_query: CallbackQuery,
    state: FSMContext,
    user: TelegramUser,
    partner: Partner = None,
):
    vacancy_id = callback_query.data.split(":")[-1]
    await state.update_data(vacancy_id=vacancy_id)

    current_state = await state.get_state()
    if current_state and current_state.startswith(TrainingCandidateForm.__name__):
        message, _, _ = await get_bot_message("vacancy_info")
        vacancy, city = await get_vacancy(user, state, partner)
        bot_text = message.format(city_name=city.name, conditions=vacancy.conditions)
        candidates = await get_applies_by_vacancy(vacancy=vacancy, partner=partner)
        if candidates:
            bot_text += "\n\nКандидаты:\n"
            for candidate in candidates:
                bot_text += f"-Имя: {candidate.full_name}\nНомер телефона: {candidate.phone_number}\n\n"

        await callback_query.message.edit_text(bot_text)
        await callback_query.answer()

    elif current_state and current_state.startswith(ApplicationForm.__name__):
        data = await state.get_data()
        city = await City.objects.aget(id=data.get("city_id"))
        msg, _, _ = await get_bot_message("city_selected_referral_fullname")
        await callback_query.message.edit_text(
            msg.format(city_name=city.name if city else "----")
            or "Пожалуйста, введите полностью Имя и Фамилию через пробел:"
        )
        await state.set_state(ApplicationForm.WaitingForFullName)
        await callback_query.answer()
