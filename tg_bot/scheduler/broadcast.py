import logging

from aiogram import Bot, exceptions
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.db.models import Q
from django.utils import timezone

from broadcast.models import BroadcastMessage
from users.models import TelegramUser


async def send_scheduled_messages(bot: Bot):
    # Ensure the database connections are valid
    close_old_connections()
    now = timezone.now()
    messages_to_send = await sync_to_async(list)(
        BroadcastMessage.objects.filter(Q(scheduled_time__lte=now) & Q(is_sent=False))
    )
    users = await sync_to_async(list)(TelegramUser.objects.all())

    for message in messages_to_send:
        for user in users:
            try:
                if message.attachments:
                    file = FSInputFile(message.attachments.path)
                    await bot.send_document(
                        chat_id=user.telegram_id,
                        document=file,
                        caption=message.message_text,
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id, text=message.message_text
                    )
            except exceptions.TelegramAPIError as e:
                logging.error(
                    f"Ошибка при отправке сообщения пользователю {user.telegram_id}: {e}"
                )
            except Exception as e:
                logging.error(
                    f"Непредвиденная ошибка при отправке сообщения пользователю {user.telegram_id}: {e}"
                )

        message.is_sent = True
        await sync_to_async(message.save)()
