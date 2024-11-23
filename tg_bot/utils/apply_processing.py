import os
from datetime import datetime

from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.files import File

from adminpanel.constants import ProcessingApplicationType
from apps.applications.models import Document, ProcessingApplication
from apps.users.models import Partner, TelegramUser
from apps.vacancies.models import Vacancy
from tg_bot.tasks import send_notification_to_channels, send_to_bitrix
from tg_bot.utils.bot_config import (
    create_reply_markup,
    get_bot_message,
    send_bot_message,
)


async def presave_application(
    state, message, user: TelegramUser, partner: Partner = None
):
    data = await state.get_data()
    if not data.get("vacancy_id"):
        vacancy, _ = await database_sync_to_async(Vacancy.objects.get_or_create)(
            name="Курьер", city_id=None
        )
    application = await database_sync_to_async(ProcessingApplication.objects.create)(
        user=user,
        partner=partner,
        full_name=data.get("full_name"),
        phone_number=data.get("phone_number"),
        city_id=data.get("city_id"),
        vacancy_id=data.get("vacancy_id") or vacancy.id,
        source=(ProcessingApplicationType.REFERRAL if data.get("referral") else None),
    )
    await state.update_data(application_id=application.id)

    # Планируем задачу на финализацию заявки через 24 часа
    from tg_bot.tasks import finalize_application_task

    finalize_application_task.apply_async(
        args=[application.id], countdown=60 * 60 * 24
    )  # 86400 секунд = 24 часа


async def finalize_application(
    state: FSMContext, message, user: TelegramUser, partner: Partner = None
):
    data = await state.get_data()
    if not data.get("vacancy_id"):
        vacancy, _ = await sync_to_async(Vacancy.objects.get_or_create)(
            name="Курьер", city_id=None
        )
    source = (
        ProcessingApplicationType.REFERRAL
        if data.get("referral") and data.get("referral") == True
        else data.get("application_type")
    )

    application_data = {
        "user": user,
        "partner": partner,
        "full_name": data.get("full_name"),
        "phone_number": data.get("phone_number"),
        "city_id": data.get("city_id"),
        "vacancy_id": data.get("vacancy_id") or vacancy.id,
        "tax_status": data.get("tax_status"),
        "car_tonnage": data.get("car_tonnage"),
        "source": source,
        "invited_date": data.get("appointment_date"),
    }

    if data.get("application_id"):
        application = await database_sync_to_async(ProcessingApplication.objects.get)(
            id=data.get("application_id")
        )
        if application.is_finalized:
            await send_bot_message(
                message, "Заявка уже была обработана. Спасибо за обращение."
            )
            return
        else:
            for field, value in application_data.items():
                setattr(application, field, value)
            application.is_finalized = True
            await database_sync_to_async(application.save)()
    else:
        application_data["is_finalized"] = True
        application = await database_sync_to_async(
            ProcessingApplication.objects.create
        )(**application_data)

    # Обработка загруженных документов
    uploaded_documents = data.get("uploaded_documents", [])
    for doc in uploaded_documents:
        document_type = doc["document_type"]
        files_received = doc["files_received"]
        for idx, file_info in enumerate(files_received, start=1):
            file_path = file_info["file_path"]
            filename = file_info.get("filename") or os.path.basename(file_path)

            with open(file_path, "rb") as f:
                django_file = File(f)
                django_file.name = filename

                await sync_to_async(Document.objects.create)(
                    application=application,
                    document_type=document_type,
                    file=django_file,
                    uploaded_at=datetime.now(tz=None),
                )

            os.remove(file_path)

    # Отправка сообщения пользователю
    bot_message_text, media, buttons = await get_bot_message(
        "application_submitted_success"
    )
    if not bot_message_text:
        bot_message_text = "Заявка успешно отправлена, с Вами скоро свяжутся."

    if source == "funnel_agency" or source == "funnel_cpa":
        send_notification_to_channels.delay(application.id)
    if source == "referral":
        send_to_bitrix.delay(application.id)

    reply_markup = create_reply_markup(buttons)

    await send_bot_message(message, bot_message_text, media, reply_markup, user)
    await state.clear()
