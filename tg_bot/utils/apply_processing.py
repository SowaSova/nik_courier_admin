import os
from datetime import datetime

from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.core.files import File

from adminpanel.constants import ProcessingApplicationType
from applications.models import Document, ProcessingApplication
from tg_bot.utils.bot_config import (
    create_reply_markup,
    get_bot_message,
    send_bot_message,
)
from users.models import Partner, TelegramUser
from vacancies.models import Vacancy


async def finalize_application(state: FSMContext, message, user: TelegramUser):
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
    application = await sync_to_async(ProcessingApplication.objects.create)(
        user=user,
        full_name=data.get("full_name"),
        phone_number=data.get("phone_number"),
        city_id=data.get("city_id"),
        vacancy_id=data.get("vacancy_id") or vacancy.id,
        tax_status=data.get("tax_status"),
        car_tonnage=data.get("car_tonnage"),
        source=source,
        invited_date=data.get("appointment_date"),
    )
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
    bot_message_text, media, buttons = await get_bot_message(
        "application_submitted_success"
    )
    if not bot_message_text:
        bot_message_text = "Заявка успешно отправлена, с Вами скоро свяжутся."

    reply_markup = create_reply_markup(buttons)

    # Отправляем сообщение пользователю
    await send_bot_message(message, bot_message_text, media, reply_markup, user)
    await state.clear()
