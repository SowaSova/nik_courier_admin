from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from adminpanel.constants import MediaType
from apps.bot.models import BotButton, BotMedia, BotMessage


async def get_bot_message(
    identifier: str,
) -> Tuple[Optional[str], Optional[BotMedia], List[BotButton]]:
    try:
        bot_message = await BotMessage.objects.select_related("media").aget(
            identifier__name=identifier
        )
        buttons = await sync_to_async(list)(bot_message.buttons.order_by("order").all())
        media = bot_message.media
        return bot_message.text, media, buttons
    except BotMessage.DoesNotExist:
        return None, None, []


def create_reply_markup(
    buttons: List[BotButton],
) -> Optional[InlineKeyboardMarkup]:
    if not buttons:
        return None
    builder = InlineKeyboardBuilder()
    for button in sorted(buttons, key=lambda x: x.order):
        builder.add(
            InlineKeyboardButton(text=button.text, callback_data=button.payload)
        )
    if len(buttons) % 2 == 1:
        builder.adjust(1)
    if len(buttons) % 2 == 0:
        builder.adjust(2)
    return builder.as_markup()


async def send_bot_message(
    message: Message,
    text: str,
    media: Optional[BotMedia],
    reply_markup,
    user,
    **format_kwargs,
):
    text = text.format(name=user.tg_username, **format_kwargs)
    if media:
        file = FSInputFile(media.file.path)
        if media.media_type == MediaType.PHOTO:
            await message.answer_photo(
                photo=file, caption=text, reply_markup=reply_markup
            )
        elif media.media_type == MediaType.VIDEO:
            await message.answer_video(
                video=file, caption=text, reply_markup=reply_markup
            )
        else:
            await message.answer_document(
                document=file, caption=text, reply_markup=reply_markup
            )
    else:
        await message.answer(text=text, reply_markup=reply_markup)


def with_bot_message(identifier: str):
    def decorator(handler: Callable[..., Any]):
        @wraps(handler)
        async def wrapper(message: Message, *args, **kwargs):
            bot_message_text, media, buttons = await get_bot_message(identifier)
            kwargs.update(
                {
                    "bot_message_text": bot_message_text,
                    "media": media,
                    "buttons": buttons,
                }
            )
            return await handler(message, *args, **kwargs)

        return wrapper

    return decorator
