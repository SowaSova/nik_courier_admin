import logging

import requests
from aiogram import Bot, exceptions
from aiogram.types import FSInputFile
from asgiref.sync import async_to_sync
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from adminpanel.constants import ProcessingApplicationType
from apps.applications.models import ProcessingApplication
from apps.broadcast.models import BroadcastMessage
from apps.users.models import TelegramChannel, TelegramUser

logger = logging.getLogger(__name__)


@shared_task
def send_to_bitrix(application_id):
    from apps.applications.models import Document, ProcessingApplication
    from tg_bot.utils.bitrix import (
        attach_files_to_deal,
        attach_files_to_lead,
        create_lead_in_bitrix,
        upload_documents_to_bitrix,
    )

    try:
        application = ProcessingApplication.objects.get(id=application_id)
    except ProcessingApplication.DoesNotExist:
        logger.error(f"Заявка с id {application_id} не найдена.")
        return

    # Создаем лид
    lead_id = create_lead_in_bitrix(application)

    if lead_id:
        application.bitrix_lead_id = lead_id
        application.save()

        # Проверяем наличие документов
        has_documents = Document.objects.filter(application=application).exists()

        if has_documents:
            # Загружаем документы и получаем их IDs
            file_ids = upload_documents_to_bitrix(application)
            attach_files_to_lead(lead_id, file_ids)

        else:
            logger.error("Нет документов для загрузки.")
    else:
        logger.error("Не удалось создать лид в Битрикс24.")


@shared_task(bind=True, max_retries=3)
def send_notification_to_channels(self, application_id):
    try:
        application = ProcessingApplication.objects.get(id=application_id)
    except ProcessingApplication.DoesNotExist:
        logger.error(f"Заявка с id {application_id} не найдена.")
        return

    # Формируем сообщение
    full_name = application.full_name
    phone_number = application.phone_number
    appointment_date = (
        application.invited_date.strftime("%d-%m-%Y")
        if application.invited_date
        else "N/A"
    )
    source = ProcessingApplicationType(application.source).label
    message_text = (
        f"📝 ❗Новая заявка ❗\n\n"
        f"ФИО: {full_name}\n"
        f"Телефон: {phone_number}\n"
        f"Дата записи: {appointment_date}\n"
        f"Источник: {application.partner}({source})"
    )

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    telegram_channels = TelegramChannel.objects.all()
    if not telegram_channels.exists():
        logger.error("Нет активных каналов Telegram.")
        return
    for chat_id in telegram_channels.values_list("chat_id", flat=True):
        payload = {
            "chat_id": chat_id,
            "text": str(message_text),
        }
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Сообщение успешно отправлено в канал {chat_id}.")
        except requests.exceptions.RequestException as e:
            # Логируем ошибку
            logger.error(f"Ошибка при отправке сообщения в канал {chat_id}: {e}")
            # Получаем статус-код ответа, если он доступен
            status_code = getattr(e.response, "status_code", None)
            response_text = getattr(e.response, "text", "")

            if status_code:
                logger.error(f"Ответ Telegram API: {response_text}")
            else:
                logger.error("Нет ответа от Telegram API.")

            # Проверяем статус-код и решаем, повторять ли попытку
            if status_code in [500, 502, 503, 504, 404]:
                # Серверные ошибки или Telegram API недоступен
                try:
                    # Повторяем попытку через 5 минут (300 секунд)
                    raise self.retry(exc=e, countdown=300)
                except MaxRetriesExceededError:
                    logger.error(
                        f"Превышено максимальное количество попыток отправки в канал {chat_id}."
                    )
            elif status_code == 429:
                # Превышено ограничение запросов
                retry_after = int(e.response.headers.get("Retry-After", 60))
                try:
                    raise self.retry(exc=e, countdown=retry_after)
                except MaxRetriesExceededError:
                    logger.error(
                        f"Превышено максимальное количество попыток отправки в канал {chat_id} после 429 Too Many Requests."
                    )
            else:
                # Для других ошибок не повторяем попытку
                logger.error(
                    f"Не удалось отправить сообщение в канал {chat_id}, код ошибки: {status_code}"
                )
            continue


@shared_task
def send_scheduled_messages():
    bot = Bot(token=settings.BOT_TOKEN)
    now = timezone.now()
    messages_to_send = list(
        BroadcastMessage.objects.filter(Q(scheduled_time__lte=now) & Q(is_sent=False))
    )

    if not messages_to_send:
        logging.info("Нет сообщений для отправки")
        async_to_sync(bot.session.close)()
        return

    for message in messages_to_send:
        # Если указан город, фильтруем по нему
        if message.city:
            # Выбираем пользователей, у которых есть ProcessingApplication с нужным городом
            users = TelegramUser.objects.filter(
                is_partner=False, processing_application__city=message.city
            ).distinct()
        else:
            # Если город не указан, берем всех пользователей без партнера
            users = TelegramUser.objects.filter(is_partner=False)

        for user in users:
            try:
                if message.attachments:
                    file = FSInputFile(message.attachments.path)
                    async_to_sync(bot.send_document)(
                        chat_id=user.telegram_id,
                        document=file,
                        caption=message.message_text,
                    )
                else:
                    async_to_sync(bot.send_message)(
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

        # Помечаем сообщение как отправленное
        message.is_sent = True
        message.save()

    async_to_sync(bot.session.close)()


@shared_task
def finalize_application_task(application_id):
    from apps.applications.models import ProcessingApplication

    application = ProcessingApplication.objects.get(id=application_id)
    if not application.is_finalized:
        # Финализируем заявку
        application.is_finalized = True
        application.save()
        # Отправляем заявку в Битрикс
        send_to_bitrix.delay(application.id)
