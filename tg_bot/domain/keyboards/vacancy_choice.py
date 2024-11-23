from asgiref.sync import sync_to_async

from apps.vacancies.models import Vacancy
from tg_bot.domain.callbacks import PaginationCallback, VacancyCallback
from tg_bot.utils import PaginationKeyboard


async def send_vacancies_keyboard(page: int = 1, city_id: int = None):
    try:
        # Получаем список вакансий для выбранного города
        vacancies = await sync_to_async(list)(Vacancy.objects.filter(city_id=city_id))

        # Проверяем, есть ли вакансии
        if not vacancies:
            return None  # Возвращаем None, если вакансий нет

        # Формируем список элементов для клавиатуры
        items = [{"id": vacancy.id, "text": vacancy.name} for vacancy in vacancies]

        # Создаем клавиатуру с пагинацией
        keyboard = PaginationKeyboard(
            items=items,
            item_callback=VacancyCallback,
            pagination_callback=PaginationCallback,
            entity="vacancy",
            city_id=city_id,
            page=page,
        ).get_keyboard()

        return keyboard
    except Exception as e:
        # Логируем ошибку, если необходимо
        # Например: logger.error(f"Error fetching vacancies: {e}")
        return None  # В случае ошибки также возвращаем None
