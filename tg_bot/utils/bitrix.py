import logging

import requests
from django.conf import settings
from django.db import transaction

from adminpanel.constants import ProcessingApplicationType
from apps.users.models import Partner

logger = logging.getLogger(__name__)


def create_lead_in_bitrix(application):
    import requests
    from django.conf import settings

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.lead.add.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    source = "1914"  # РЕФЕРАЛЬНЫЙ (ТГ)
    name = application.full_name.split(" ")[0]
    last_name = application.full_name.split(" ")[1]
    if not application.partner.btx_id:
        with transaction.atomic():
            partner = Partner.objects.select_for_update().get(id=application.partner.id)
            if not partner.btx_id:
                # Create responsible person in Bitrix24
                partner.btx_id = create_responsible_person_in_bitrix(partner)
                partner.save()

    title = f"{application.partner}_{application.city.name}_{name}_{last_name}"
    data = {
        "fields": {
            "TITLE": title,
            "NAME": name,
            "LAST_NAME": last_name,
            "PHONE": [{"VALUE": application.phone_number, "VALUE_TYPE": "WORK"}],
            "UF_CRM_1727558363198": application.city.btx_id,  # Город кандидата
            # "UF_CRM_1732013449": application.vacancy.name,  # Вакансия
            "UF_CRM_1727558842072": application.car_tonnage,  # Грузоподъемность
            "UF_CRM_1727558736573": application.tax_status,  # Статус налогоплательщика
            "UF_CRM_1727559062022": source,  # Канал поступления
            "UF_CRM_1727557777158": application.partner.btx_id,  # Партнер
            "UF_CRM_1727558891776": (
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


def get_userfield_id_by_name(field_name):
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.lead.userfield.list.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    response = requests.get(url)
    response.raise_for_status()
    result = response.json()
    if "result" in result:
        for field in result["result"]:
            if field["FIELD_NAME"] == field_name:
                return field["ID"]
        raise Exception(f"User field with FIELD_NAME '{field_name}' not found")
    else:
        error = result.get("error_description", "Unknown error")
        raise Exception(f"Bitrix24 API error: {error}")


def get_userfield(field_id):
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.lead.userfield.get.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    params = {"id": field_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()
    if "result" in result:
        return result["result"]
    else:
        error = result.get("error_description", "Unknown error")
        raise Exception(f"Bitrix24 API error: {error}")


def add_new_item_to_list(current_list, partner):
    process_type = ProcessingApplicationType
    new_value = f"{partner.name} ({process_type(partner.proccess_type).label})"
    # Проверяем, существует ли элемент с таким значением
    for item in current_list:
        if item["VALUE"] == new_value:
            return current_list  # Элемент уже существует
    new_item = {
        "VALUE": new_value,
        "DEF": "N",
        "SORT": "500",
    }
    updated_list = current_list.copy()
    updated_list.append(new_item)
    return updated_list


def update_userfield(field_id, updated_list):
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )
    method = "crm.lead.userfield.update.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    data = {"id": field_id, "fields": {"LIST": updated_list}}
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
    if "result" in result:
        return True
    else:
        error = result.get("error_description", "Unknown error")
        raise Exception(f"Bitrix24 API error: {error}")


def get_new_item_id(field_data, partner):
    process_type = ProcessingApplicationType
    new_value = f"{partner.name} ({process_type(partner.proccess_type).label})"
    for item in field_data["LIST"]:
        if item["VALUE"] == new_value:
            return item["ID"]
    raise Exception("New item ID not found")


@transaction.atomic
def create_responsible_person_in_bitrix(partner):
    field_name = "UF_CRM_1727557777158"  # Символьный код поля
    # Получаем числовой ID пользовательского поля
    field_id = get_userfield_id_by_name(field_name)

    # Шаг 1: Получаем текущее поле
    try:
        field_data = get_userfield(field_id)
        current_list = field_data.get("LIST", [])
        # Убедимся, что у всех существующих элементов есть ID
        for item in current_list:
            if "ID" not in item:
                item["ID"] = item.get("ID")
    except Exception as e:
        logger.error(f"Ошибка при получении пользовательского поля: {e}")
        raise

    # Шаг 2: Добавляем новый элемент в список
    try:
        updated_list = add_new_item_to_list(current_list, partner)
    except Exception as e:
        logger.error(f"Ошибка при добавлении нового элемента в список: {e}")
        raise

    # Шаг 3: Обновляем поле с новым списком
    try:
        update_userfield(field_id, updated_list)
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользовательского поля: {e}")
        raise

    # Шаг 4: Получаем ID нового элемента
    try:
        updated_field_data = get_userfield(field_id)
        btx_id = get_new_item_id(updated_field_data, partner)
        return btx_id
    except Exception as e:
        logger.error(f"Ошибка при получении ID нового элемента: {e}")
        raise


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
    from apps.applications.models import Document

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
            "UF_CRM_1732522425": file_ids,  # Замените на реальный код пользовательского поля для файлов в сделке
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


def attach_files_to_lead(lead_id, file_id):
    import requests
    from django.conf import settings

    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM  # Убедитесь, что у вас правильный токен
    )
    method = "crm.lead.update.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    data = {
        "id": lead_id,
        "fields": {
            "UF_CRM_1732522425": file_id,  # Замените на реальный код пользовательского поля для файлов в сделке
        },
        "params": {"REGISTER_SONET_EVENT": "Y"},
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        if result.get("result"):
            logger.info(f"Файл успешно привязан к лиду {lead_id}.")
        else:
            logger.error(f"Ошибка при привязке файла к лиду: {result}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при привязке файла к лиду: {e}")
