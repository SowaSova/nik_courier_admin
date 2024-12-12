# from datetime import datetime

# from aiogram import F, Router
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery

# from apps.users.models import Partner, TelegramUser
# from tg_bot.domain.keyboards import create_calendar
# from tg_bot.domain.keyboards.city_choice import send_cities_keyboard
# from tg_bot.domain.states.application import ApplicationForm
# from tg_bot.domain.states.personal_cabinet import PersonalCabinetForm
# from tg_bot.utils import finalize_application
# from tg_bot.utils.bot_config import get_bot_message

# router = Router()


# @router.callback_query(
#     F.data.in_(
#         [
#             "back_to_city_choice",
#             "back_to_vacancy_choice",
#             "back_to_main_menu",
#         ]
#     )
# )
# async def back_to(callback_query: CallbackQuery, state: FSMContext):
#     if callback_query.data == "back_to_city_choice":
#         await callback_query.message.edit_text(
#             "Выберите город:", reply_markup=await send_cities_keyboard()
#         )
#     if callback_query.data == "back_to_name":
#         bot_message_text, media, buttons = await get_bot_message(
#             "city_selected_referral_fullname"
#         )
#         await callback_query.message.edit_text()
#     # if callback_query.data == "back_to_main_menu":
#     #     await state.clear()
#     #     await callback_query.message.edit_text("Выберите город:", reply_markup=await send_cities_keyboard())
