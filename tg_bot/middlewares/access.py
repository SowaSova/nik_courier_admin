from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, Update
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from apps.users.models import Partner, TelegramUser


class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        user = None
        partner = None

        if event.message:
            from_user = event.message.from_user
        elif event.callback_query:
            from_user = event.callback_query.from_user
        else:
            return await handler(event, data)

        telegram_id = from_user.id
        username = from_user.username

        user, created = await database_sync_to_async(
            TelegramUser.objects.get_or_create
        )(telegram_id=telegram_id, defaults={"tg_username": username})

        if not user.telegram_id:
            user.telegram_id = telegram_id
            await sync_to_async(user.save)()
        if not user.invited_by_id:
            user.invited_by = user
            await sync_to_async(user.save)()

        if not user.is_verified:
            if event.message and event.message.text.startswith("/start "):
                start_param = event.message.text.split(" ", 1)[1]
                try:
                    partner = await database_sync_to_async(Partner.objects.get)(
                        referal_idx=start_param
                    )

                    user.is_verified = True
                    user.invited_by_id = partner.user_id
                    await sync_to_async(user.save)()
                except Partner.DoesNotExist:
                    await event.message.answer(
                        "Неверная или устаревшая реферальная ссылка."
                    )
                    return
            else:
                if event.message:
                    await event.message.answer(
                        "Для доступа к боту вам нужно перейти по реферальной ссылке. Если у вас её нет, обратитесь к администратору."
                    )
                elif event.callback_query:
                    await event.callback_query.answer(
                        "Для доступа к боту вам нужно перейти по реферальной ссылке.",
                        show_alert=True,
                    )
                return
        try:
            data["partner"] = await Partner.objects.aget(pk=user.invited_by_id)
        except Partner.DoesNotExist:
            data["partner"] = None
        data["user"] = user
        return await handler(event, data)
