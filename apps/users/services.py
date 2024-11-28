import logging

import requests
from django.conf import settings
from django.db import transaction

from adminpanel.constants import ProcessingApplicationType

logger = logging.getLogger(__name__)


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
