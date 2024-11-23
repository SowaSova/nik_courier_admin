import logging

logger = logging.getLogger(__name__)


def create_lead_in_bitrix(application):
    import requests
    from django.conf import settings

    from apps.applications.models import ProcessingApplicationType

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.lead.add.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    source = ProcessingApplicationType(application.source).label
    data = {
        "fields": {
            "TITLE": f"Лид от {application.partner}",
            "NAME": application.full_name,
            "PHONE": [{"VALUE": application.phone_number, "VALUE_TYPE": "WORK"}],
            "ADDRESS": application.city.name,
            "UF_CRM_1732013449": application.vacancy.name,  # Вакансия
            "UF_CRM_1732012920": application.car_tonnage,  # Грузоподъемность
            "UF_CRM_1732013460": application.tax_status,  # Статус налогоплательщика
            "UF_CRM_1732013470": source,  # Источник(воронка)
            "UF_CRM_1732013482": (
                application.invited_date.strftime("%Y-%m-%d")
                if application.invited_date
                else None
            ),  # Дата записи
        }
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "result" in result:
            lead_id = result["result"]
            logger.info(f"Лид успешно создан в Битрикс24 с ID {lead_id}.")
            return lead_id
        else:
            logger.error(f"Ошибка при создании лида в Битрикс24: {result}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к Битрикс24: {e}")
        return None


def upload_file_to_bitrix(document):
    import base64
    import os

    import requests
    from django.conf import settings

    logger = logging.getLogger(__name__)

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_FILES
    )
    method = "disk.folder.uploadFile"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    folder_id = settings.BITRIX_FOLDER_ID  # Укажите ID папки в настройках

    # Получаем путь к файлу
    file_path = document.file.path
    file_name = os.path.basename(file_path)

    # Шаг 1: Получение 'uploadUrl' и 'field'
    params = {"id": folder_id}
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            encoded_content = base64.b64encode(file_content).decode("utf-8")
            return {"fileData": [file_name, encoded_content]}
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_name}: {e}")
        return None


def upload_documents_to_bitrix(application):
    from applications.models import Document

    documents = Document.objects.filter(application=application)

    file_ids = []

    for document in documents:
        file_id = upload_file_to_bitrix(document)
        if file_id:
            file_ids.append(file_id)
        else:
            logger.error(f"Не удалось загрузить файл {document.file.name} в Битрикс24.")

    return file_ids


def get_deal_id_from_lead(lead_id):
    import requests
    from django.conf import settings

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.deal.list.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    params = {"filter": {"LEAD_ID": lead_id}, "select": ["ID"]}

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        result = response.json()
        if "result" in result and result["result"]:
            deal_id = result["result"][0]["ID"]
            logger.info(f"Сделка с ID {deal_id} найдена для лида {lead_id}.")
            return deal_id
        else:
            logger.error(f"Сделка для лида {lead_id} не найдена.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении сделки для лида {lead_id}: {e}")
        return None


def attach_files_to_deal(deal_id, file_ids):
    import requests
    from django.conf import settings

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM  # Убедитесь, что у вас правильный токен
    )
    method = "crm.deal.update.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    data = {
        "id": deal_id,
        "fields": {
            "UF_CRM_673D936E88F7C": file_ids,  # Замените на реальный код пользовательского поля для файлов в сделке
        },
        "params": {"REGISTER_SONET_EVENT": "Y"},
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        if result.get("result"):
            logger.info(f"Файлы успешно привязаны к сделке {deal_id}.")
        else:
            logger.error(f"Ошибка при привязке файлов к сделке: {result}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при привязке файлов к сделке: {e}")
