from aiogram import F, Router
from aiogram.types import CallbackQuery

from adminpanel.constants import ProcessingApplicationType
from apps.users.models import Partner
from tg_bot.domain.keyboards.city_choice import send_cities_keyboard
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.bot_config import get_bot_message

router = Router()


@router.callback_query(F.data == "start_application")
async def process_start_application(
    callback_query: CallbackQuery, state: ApplicationForm, partner: Partner
):
    partner_application = partner.proccess_type
    application_type = (
        ProcessingApplicationType.FUNNEL_AGENCY
        if partner_application == "funnel_agency"
        else ProcessingApplicationType.FUNNEL_CPA
    )
    await state.update_data(application_type=application_type)
    cities_kb = await send_cities_keyboard()
    if not cities_kb:
        msg = await get_bot_message("cities_not_found")
        await callback_query.message.answer(msg or "Нет доступных городов")
        return
    await callback_query.message.answer("Выберите город:", reply_markup=cities_kb)
    await state.set_state(ApplicationForm.WaitingForCityChoice)
    await callback_query.answer()
