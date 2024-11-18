import os
import tempfile
from typing import Union

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from adminpanel.constants import DocumentType, TaxStatus
from tg_bot.domain.keyboards import create_calendar
from tg_bot.domain.states import ApplicationForm
from tg_bot.utils.apply_processing import finalize_application
from tg_bot.utils.bot_config import get_bot_message, send_bot_message
from users.models import TelegramUser

router = Router()

document_requirements = {
    DocumentType.LICENSE: ["Лицевая сторона", "Оборотная сторона"],
    DocumentType.PASSPORT: ["Первая страница", "Страница с пропиской"],
    DocumentType.REGISTRATION: ["Фото регистрации"],
    DocumentType.TAX_DOCUMENT: ["Налоговый документ"],
}


@router.callback_query(ApplicationForm.WaitingForDocumentChoice)
async def process_document_choice(
    callback_query: CallbackQuery, state: FSMContext, user: TelegramUser
):
    choice = callback_query.data
    if choice == "upload_now":
        data = await state.get_data()
        tax_status = data.get("tax_status")
        required_documents = [
            DocumentType.LICENSE,
            DocumentType.PASSPORT,
            DocumentType.REGISTRATION,
        ]

        if tax_status in [TaxStatus.SMZ, TaxStatus.IP]:
            required_documents.append(DocumentType.TAX_DOCUMENT)

        pending_documents = []
        for doc_type in required_documents:
            descriptions = document_requirements.get(doc_type, ["1-й файл"])
            pending_documents.append(
                {
                    "document_type": doc_type,
                    "files_needed": len(descriptions),
                    "files_descriptions": descriptions,
                    "files_received": [],
                }
            )

        await state.update_data(pending_documents=pending_documents)
        await prompt_for_next_document(callback_query.message, state, user)
        await state.set_state(ApplicationForm.WaitingForDocuments)
    elif choice == "schedule_date":
        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message(
            "choose_date_for_documents"
        )
        if not bot_message_text:
            bot_message_text = (
                "Пожалуйста, выберите дату для предоставления документов."
            )

        reply_markup = create_calendar()
        await callback_query.message.answer(bot_message_text, reply_markup=reply_markup)
        await state.set_state(ApplicationForm.WaitingForAppointmentDate)
    await callback_query.answer()


@router.message(
    ApplicationForm.WaitingForDocuments,
    F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}),
)
async def process_document_upload(
    message: Message, state: FSMContext, user: TelegramUser
):
    data = await state.get_data()
    pending_documents = data.get("pending_documents", [])

    if not pending_documents:
        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message("no_pending_documents")
        if not bot_message_text:
            bot_message_text = "Нет ожидаемых документов."

        await send_bot_message(message, bot_message_text, media, None, user)
        return

    current_document = pending_documents[0]
    doc_type = current_document["document_type"]

    if message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        file_unique_id = message.photo[-1].file_unique_id
        filename = f"{file_unique_id}.jpg"
    elif message.content_type == ContentType.DOCUMENT:
        file_id = message.document.file_id
        file_unique_id = message.document.file_unique_id
        filename = message.document.file_name
    else:
        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message("invalid_file_type")
        if not bot_message_text:
            bot_message_text = (
                "Неверный тип файла. Пожалуйста, отправьте фото или документ."
            )

        await send_bot_message(message, bot_message_text, media, None, user)
        return

    temp_dir = tempfile.gettempdir()
    file_name = f"{file_unique_id}"
    file_path = os.path.join(temp_dir, file_name)

    await download_file(message.bot, file_id, file_path)

    current_document["files_received"].append(
        {
            "file_path": file_path,
            "content_type": message.content_type,
            "filename": filename,
        }
    )

    if len(current_document["files_received"]) >= current_document["files_needed"]:
        pending_documents.pop(0)
        await state.update_data(pending_documents=pending_documents)

        uploaded_documents = data.get("uploaded_documents", [])
        uploaded_documents.append(current_document)
        await state.update_data(uploaded_documents=uploaded_documents)
    else:
        pending_documents[0] = current_document
        await state.update_data(pending_documents=pending_documents)

    if pending_documents:
        await prompt_for_next_document(message, state, user)
    else:
        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message(
            "all_documents_received"
        )
        if not bot_message_text:
            bot_message_text = "Спасибо, все документы получены."

        await send_bot_message(message, bot_message_text, media, None, user)
        await finalize_application(state, message, user)


async def prompt_for_next_document(
    message: Message, state: FSMContext, user: TelegramUser
):
    data = await state.get_data()
    pending_documents = data.get("pending_documents")

    if pending_documents:
        current_document = pending_documents[0]
        doc_type = current_document["document_type"]
        files_received = len(current_document["files_received"])
        descriptions = current_document.get("files_descriptions", [])
        description = (
            descriptions[files_received]
            if descriptions
            else f"{files_received + 1}-й файл"
        )

        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message(
            "prompt_for_document_upload"
        )
        if not bot_message_text:
            bot_message_text = (
                "Пожалуйста, отправьте {description} для {document_label}."
            )

        # Форматируем сообщение с необходимыми переменными
        message_text = bot_message_text.format(
            description=description,
            document_label=DocumentType(doc_type).label,
        )

        await send_bot_message(message, message_text, media, None, user)
    else:
        # Получаем сообщение из базы данных
        bot_message_text, media, buttons = await get_bot_message(
            "all_documents_received"
        )
        if not bot_message_text:
            bot_message_text = "Спасибо, все документы получены."

        await send_bot_message(message, bot_message_text, media, None, user)


async def download_file(bot, file_id, destination):
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination)
