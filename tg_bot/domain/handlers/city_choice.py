from typing import Union

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async

from geo.models import City
from tg_bot.domain.callbacks import CityCallback
from tg_bot.domain.keyboards import create_calendar
from tg_bot.domain.keyboards.vacancy_choice import send_vacancies_keyboard
from tg_bot.domain.states import ApplicationForm
from tg_bot.domain.states.personal_cabinet import PersonalCabinetForm
from tg_bot.utils.bot_config import get_bot_message
from users.models import TelegramUser

router = Router()


@router.callback_query(CityCallback.filter())
async def city_selected(
    callback_query: CallbackQuery,
    callback_data: CityCallback,
    state: FSMContext,
    user: TelegramUser,
):
    current_state = await state.get_state()
    data = await state.get_data()
    city_id = callback_data.id
    try:
        city = await sync_to_async(City.objects.get)(id=city_id)
    except City.DoesNotExist:
        await callback_query.answer("Город не найден", show_alert=True)
        return

    await state.update_data(city_id=city_id)

    if current_state and current_state.startswith(ApplicationForm.__name__):
        if data.get("referral"):
            # Получаем сообщение для 'city_selected_referral_fullname'
            bot_message_text, media, buttons = await get_bot_message(
                "city_selected_referral_fullname"
            )
            if not bot_message_text:
                bot_message_text = "Вы выбрали город: {city_name}. Пожалуйста, введите полностью Ваше ФИО:"

            message_text = bot_message_text.format(city_name=city.name)
            await callback_query.message.edit_text(message_text)
            await state.set_state(ApplicationForm.WaitingForFullName)
        else:
            # Получаем сообщение для 'city_selected_choose_vacancy'
            bot_message_text, media, buttons = await get_bot_message(
                "city_selected_choose_vacancy"
            )
            if not bot_message_text:
                bot_message_text = (
                    "Вы выбрали город: {city_name}. Пожалуйста, выберите вакансию:"
                )

            message_text = bot_message_text.format(city_name=city.name)
            vacancies_keyboard = await send_vacancies_keyboard(city_id=city_id)

            await callback_query.message.edit_text(
                message_text,
                reply_markup=vacancies_keyboard,
            )
            await state.set_state(ApplicationForm.WaitingForVacancyChoice)
    elif current_state and current_state.startswith(PersonalCabinetForm.__name__):
        # Получаем сообщение для 'personal_cabinet_select_date'
        bot_message_text, media, buttons = await get_bot_message(
            "personal_cabinet_select_date"
        )
        if not bot_message_text:
            bot_message_text = "Выберите дату:"

        await callback_query.message.edit_text(
            bot_message_text, reply_markup=create_calendar()
        )
        await state.set_state(PersonalCabinetForm.WaitingForDate)
    else:
        # Получаем сообщение об ошибке 'unknown_state'
        bot_message_text, _, _ = await get_bot_message("unknown_state")
        if not bot_message_text:
            bot_message_text = "Неизвестное состояние"

        await callback_query.answer(bot_message_text, show_alert=True)
        return

    await callback_query.answer()
