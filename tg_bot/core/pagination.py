from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix="pag"):
    paginator_id: str
    action: str
    page: int
