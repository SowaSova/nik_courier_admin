from typing import List, Optional

from aiogram import F, Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings

from apps.bot.models import BotButton, BotMedia
from apps.users.models import Partner, TelegramUser
from tg_bot.utils import count_applies_from_referral
from tg_bot.utils.bot_config import (create_reply_markup, send_bot_message,
                                     with_bot_message)

router = Router()


@router.callback_query(F.data == "referral_links")
@with_bot_message("referral_links")
async def process_referral_links(
    callback_query: CallbackQuery,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    partner = await sync_to_async(Partner.objects.get)(user=user)
    referral_link = f"https://t.me/{settings.BOT_NAME}?start={partner.referal_idx}"
    count = await count_applies_from_referral(user, partner)

    if not bot_message_text:
        bot_message_text = (
            "<b>Ваша реферальная ссылка:</b>\n"
            "<code>{referral_link}</code>\n\n"
            "<b>Кол-во заявок:</b> {count}"
        )

    # Форматируем сообщение, подставляя динамические данные
    message_text = bot_message_text.format(
        referral_link=referral_link,
        count=count,
    )

    # Создаём клавиатуру, если есть кнопки
    reply_markup = create_reply_markup(buttons)

    # Отправляем сообщение пользователю
    await send_bot_message(
        message=callback_query.message,
        text=message_text,
        media=media,
        reply_markup=reply_markup,
        user=user,
    )

    await callback_query.answer()
