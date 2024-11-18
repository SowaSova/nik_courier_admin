from asgiref.sync import sync_to_async

from tg_bot.domain.callbacks import PaginationCallback, VacancyCallback
from tg_bot.utils import PaginationKeyboard
from vacancies.models import Vacancy


async def send_vacancies_keyboard(page: int = 1, city_id: int = None):
    try:
        vacancies = await sync_to_async(list)(Vacancy.objects.filter(city_id=city_id))
        items = [{"id": vacancy.id, "text": vacancy.name} for vacancy in vacancies]
        keyboard = PaginationKeyboard(
            items=items,
            item_callback=VacancyCallback,
            pagination_callback=PaginationCallback,
            entity="vacancy",
            city_id=city_id,
            page=page,
        ).get_keyboard()
        return keyboard
    except Vacancy.DoesNotExist:
        return None
