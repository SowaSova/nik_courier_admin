from typing import Optional

from aiogram.filters.callback_data import CallbackData


class CityCallback(CallbackData, prefix="city"):
    id: int


class PaginationCallback(CallbackData, prefix="pag"):
    action: str
    page: int
    entity: str
    city_id: Optional[int] = None


class ApplicationStatusCallback(CallbackData, prefix="status"):
    status: str


class VacancyCallback(CallbackData, prefix="vacancy"):
    id: int
