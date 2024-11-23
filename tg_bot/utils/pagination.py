from math import ceil

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tg_bot.core.constants import ITEMS_PER_PAGE


class PaginationKeyboard:
    def __init__(
        self,
        items,
        item_callback,
        pagination_callback,
        entity,
        city_id=None,
        page=1,
        items_per_page=ITEMS_PER_PAGE,
    ):
        self.items = items
        self.item_callback = item_callback
        self.pagination_callback = pagination_callback
        self.page = page
        self.items_per_page = items_per_page
        self.entity = entity
        self.city_id = city_id
        self.total_pages = ceil(len(items) / items_per_page)

    def get_keyboard(self):
        builder = InlineKeyboardBuilder()
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page
        current_items = self.items[start:end]
        for item in current_items:
            item_cb = self.item_callback(id=item["id"])
            button = InlineKeyboardButton(
                text=item["text"],
                callback_data=item_cb.pack(),
            )
            builder.row(button)

        navigation_buttons = []
        if self.page > 1:
            pagination_cb = self.pagination_callback(
                action="page",
                page=self.page - 1,
                entity=self.entity,
                city_id=self.city_id,
            )
            prev_button = InlineKeyboardButton(
                text="⏪ Назад",
                callback_data=pagination_cb.pack(),
            )
            navigation_buttons.append(prev_button)
        if self.page < self.total_pages:
            pagination_cb = self.pagination_callback(
                action="page",
                page=self.page + 1,
                entity=self.entity,
                city_id=self.city_id,
            )
            next_button = InlineKeyboardButton(
                text="Вперед ⏩",
                callback_data=pagination_cb.pack(),
            )
            navigation_buttons.append(next_button)

        if navigation_buttons:
            builder.row(*navigation_buttons)
        builder.adjust(2)
        return builder.as_markup()
