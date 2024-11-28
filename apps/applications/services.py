import logging
import re

import requests
from django.conf import settings
from django.db import transaction

from adminpanel.constants import ProcessingApplicationType
from apps.applications.models import ProcessingApplication
from apps.geo.models import City
from apps.users.models import Partner

logger = logging.getLogger(__name__)


def process_lead_update(lead_id):
    # Получаем детали лида из Bitrix24
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )  # Ваш вебхук URL для вызова методов API
    method = "crm.lead.get.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    params = {"id": lead_id}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        if "result" in result:
            lead = result["result"]
            # Передаем данные лида для обновления заявки
            update_application_from_lead(lead)
        else:
            logger.error(f"Ошибка при получении лида {lead_id}: {result}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к Bitrix24: {e}")


def update_application_from_lead(lead):
    status = lead.get("STATUS_ID")  # Получаем текущий статус лида

    try:
        # Ищем заявку по bitrix_lead_id, равному LEAD_ID из лида
        application = ProcessingApplication.objects.get(bitrix_lead_id=lead["ID"])
        old_status = application.status  # Сохраняем предыдущий статус
        new_status = map_status_from_bitrix(status)

        # Проверяем, изменился ли статус
        if old_status != new_status:
            with transaction.atomic():
                application.status = new_status
                application.save()
                logger.info(
                    f"Статус заявки {application.id} изменен с {old_status} на {new_status}"
                )
        else:
            logger.info(f"Статус заявки {application.id} не изменился")
    except ProcessingApplication.DoesNotExist:
        logger.error(f"Заявка с bitrix_lead_id={lead['ID']} не найдена.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса заявки: {e}")


def calculate_reward_difference(application, old_status, new_status):
    STATUS_REWARD_MAPPING = {
        "closed": 1000,  # Укажите сумму вознаграждения для статуса "closed"
        # Добавьте другие статусы, если требуется
    }

    old_reward = STATUS_REWARD_MAPPING.get(old_status, 0)
    new_reward = STATUS_REWARD_MAPPING.get(new_status, 0)

    reward_difference = new_reward - old_reward
    return reward_difference


def map_status_from_bitrix(bitrix_status):
    STATUS_MAPPING = {
        "NEW": "new",
        "IN_PROCESS": "active",
        "UC_5IK5JH": "active",
        "PROCESSED": "active",
        "UC_RT8PLX": "active",
        "СONVERTED": "closed",
    }
    return STATUS_MAPPING.get(bitrix_status, bitrix_status.lower())


@transaction.atomic
def update_city_list():
    cities = get_updated_city_list()
    existing_city_ids = set(City.objects.values_list("btx_id", flat=True))
    incoming_city_ids = set()

    for city_data in cities:
        btx_id = city_data["btx_id"]
        name = city_data["name"]
        incoming_city_ids.add(btx_id)
        City.objects.update_or_create(btx_id=btx_id, defaults={"name": name})

    # Удаляем города, которых нет в Bitrix24
    cities_to_delete = existing_city_ids - incoming_city_ids
    if cities_to_delete:
        City.objects.filter(btx_id__in=cities_to_delete).delete()


def get_updated_city_list():
    from apps.applications.models import City

    # Получаем список городов из Bitrix24
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )  # Ваш вебхук URL для вызова методов API
    method = "crm.lead.fields.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"
    try:
        response = requests.get(url)
        data = response.json()
        field_id = "UF_CRM_1727558363198"
        field_info = data["result"].get(field_id)
        if field_info and "items" in field_info:
            items = field_info["items"]
            cities = []
            for item in items:
                city = {"btx_id": int(item["ID"]), "name": item["VALUE"]}
                cities.append(city)
            return cities
        else:
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к Bitrix24: {e}")
        return []


def get_updated_partner_list():
    # Получаем список партнеров из Bitrix24
    BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
        token=settings.BITRIX_WH_CRM
    )  # Ваш вебхук URL для вызова методов API
    method = "crm.lead.fields.json"
    url = f"{BITRIX_WEBHOOK_URL}{method}"

    try:
        response = requests.get(url)
        data = response.json()
        field_id = "UF_CRM_1727557777158"
        field_info = data["result"].get(field_id)
        if field_info and "items" in field_info:
            items = field_info["items"]
            partners = []
            for item in items:
                value = item["VALUE"]
                # Извлекаем текст внутри скобок
                match = re.search(r"\(([^)]+)\)", value)
                if match:
                    label = match.group(1).strip()
                else:
                    label = ""
                funnel = (
                    ProcessingApplicationType.FUNNEL_AGENCY
                    if label == "Агент"
                    else ProcessingApplicationType.FUNNEL_CPA
                )
                partner = {
                    "btx_id": int(item["ID"]),
                    "name": item["VALUE"],
                    "proccess_type": funnel,
                }
                partners.append(partner)
            return partners
        else:
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к Bitrix24: {e}")
        return []


@transaction.atomic
def update_partner_list():
    partners = get_updated_partner_list()
    existing_partner_ids = set(Partner.objects.values_list("btx_id", flat=True))
    incoming_partner_ids = set()

    for city_data in partners:
        btx_id = city_data["btx_id"]
        name = city_data["name"]
        process_type = city_data["proccess_type"]
        incoming_partner_ids.add(btx_id)
        Partner.objects.update_or_create(
            btx_id=btx_id, defaults={"name": name, "proccess_type": process_type}
        )

    # Удаляем города, которых нет в Bitrix24
    cities_to_delete = existing_partner_ids - incoming_partner_ids
    if cities_to_delete:
        Partner.objects.filter(btx_id__in=cities_to_delete).delete()
