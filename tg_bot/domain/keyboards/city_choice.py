from asgiref.sync import sync_to_async

from geo.models import City
from tg_bot.domain.callbacks import CityCallback, PaginationCallback
from tg_bot.utils import PaginationKeyboard


async def send_cities_keyboard(page: int = None):
    try:
        cities = await sync_to_async(list)(City.objects.all())
        items = [{"id": city.id, "text": city.name} for city in cities]
        keyboard = PaginationKeyboard(
            items=items,
            item_callback=CityCallback,
            pagination_callback=PaginationCallback,
            entity="city",
            page=page or 1,
        ).get_keyboard()
        return keyboard
    except City.DoesNotExist:
        return None
