from aiogram import Router
from aiogram.types import CallbackQuery

from tg_bot.domain.callbacks import PaginationCallback
from tg_bot.domain.keyboards import (
    send_cities_keyboard,
    send_vacancies_keyboard,
)

router = Router()


@router.callback_query(PaginationCallback.filter())
async def paginate(
    callback_query: CallbackQuery, callback_data: PaginationCallback
):
    action = callback_data.action
    page = callback_data.page
    entity = callback_data.entity
    city_id = callback_data.city_id  # Получаем city_id, если оно есть

    if entity == "city":
        keyboard = await send_cities_keyboard(page=page)
    elif entity == "vacancy":
        if not city_id:
            await callback_query.answer(
                "Не указан город для отображения вакансий."
            )
            return
        keyboard = await send_vacancies_keyboard(page=page, city_id=city_id)
    else:
        await callback_query.answer("Неизвестный тип пагинации.")
        return

    if keyboard:
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback_query.answer("Нет доступных страниц.")
    await callback_query.answer()
