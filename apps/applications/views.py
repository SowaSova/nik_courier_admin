import json
import logging

import requests
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.applications.services import (process_lead_update, update_city_list,
                                        update_partner_list)
from apps.geo.models import City

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def bitrix_webhook(request):
    try:
        # Получаем данные из запроса
        data = request.POST
        # Проверяем наличие токена
        token = data.get("auth[application_token]")
        if not token or token != settings.BITRIX_WEBHOOK_TOKEN:
            logger.error("Некорректный или отсутствующий токен")
            return HttpResponseBadRequest("Invalid token")
        # Обрабатываем событие
        event = data.get("event")
        # if event == "ONCRMDEALUPDATE":
        #     deal_id = data.get("data[FIELDS][ID]")
        #     process_deal_update(deal_id)
        if event == "ONCRMLEADUPDATE":
            lead_id = data.get("data[FIELDS][ID]")
            # Ваш код обработки обновления лида
            process_lead_update(lead_id)
        elif event == "ONCRMLEADUSERFIELDSETENUMVALUES":
            field_name = data.get("data[FIELDS][FIELD_NAME]")
            if field_name == "UF_CRM_1727558363198":
                update_city_list()
            if field_name == "UF_CRM_1727557777158":
                update_partner_list()
        else:
            logger.warning(f"Неизвестное событие: {event}")

        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}")
        return HttpResponseBadRequest("Error processing webhook")


# def process_deal_update(deal_id):
#     import requests
#     from django.conf import settings

#     # Получаем детали сделки из Bitrix24
#     BITRIX_WEBHOOK_URL = settings.BITRIX_WEBHOOK_URL.format(
#         token=settings.BITRIX_WH_CRM
#     )  # Ваш вебхук URL для вызова методов API
#     method = "crm.deal.get.json"
#     url = f"{BITRIX_WEBHOOK_URL}{method}"

#     params = {"id": deal_id}

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         result = response.json()
#         if "result" in result:
#             deal = result["result"]
#             # Передаем данные сделки для обновления заявки
#             update_application_from_deal(deal)
#         else:
#             logger.error(f"Ошибка при получении сделки {deal_id}: {result}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Ошибка при обращении к Bitrix24: {e}")


# def update_application_from_deal(deal):
#     from django.db import transaction

#     from apps.applications.models import ProcessingApplication
#     from apps.users.models import Partner

#     lead_id = deal.get("LEAD_ID")  # Получаем LEAD_ID из данных сделки
#     status = deal.get("STAGE_ID")  # Получаем текущий статус сделки

#     if not lead_id:
#         logger.error(f"LEAD_ID отсутствует в данных сделки {deal.get('ID')}")
#         return

#     try:
#         # Ищем заявку по bitrix_lead_id, равному LEAD_ID из сделки
#         application = ProcessingApplication.objects.get(bitrix_lead_id=lead_id)
#         old_status = application.status  # Сохраняем предыдущий статус
#         new_status = map_status_from_bitrix(status)

#         # Проверяем, изменился ли статус
#         if old_status != new_status:
#             with transaction.atomic():
#                 reward_difference = calculate_reward_difference(
#                     application, old_status, new_status
#                 )

#                 # Обновляем статус и сумму вознаграждения заявки
#                 application.status = new_status
#                 application.save()

#                 if reward_difference != 0:
#                     partner = application.user.invited_by
#                     partner = Partner.objects.get(user=partner)
#                     new_balance = partner.balance + reward_difference
#                     if new_balance < 0:
#                         logger.error(
#                             f"Баланс партнера {partner.user} не может быть отрицательным"
#                         )
#                         raise ValueError("Баланс не может быть отрицательным")
#                     partner.balance = new_balance
#                     partner.save()
#                     logger.info(
#                         f"Баланс партнера {partner.user} обновлен на {reward_difference}"
#                     )
#                 logger.info(
#                     f"Статус заявки {application.id} изменен с {old_status} на {new_status}"
#                 )
#         else:
#             logger.info(f"Статус заявки {application.id} не изменился")
#     except ProcessingApplication.DoesNotExist:
#         logger.error(f"Заявка с bitrix_lead_id={lead_id} не найдена.")
#     except Exception as e:
#         logger.error(f"Ошибка при обновлении заявки: {e}")
#         # Здесь можно добавить дополнительные действия по обработке ошибки
