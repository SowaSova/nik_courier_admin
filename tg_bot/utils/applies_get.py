from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from adminpanel.constants import ApplicationStatus
from apps.applications.models import ProcessingApplication
from apps.geo.models import City
from apps.users.models import Partner, TelegramUser
from apps.vacancies.models import Vacancy


async def get_applies(
    user: TelegramUser, state: FSMContext
) -> list[ProcessingApplication]:
    data = await state.get_data()
    status = data.get("status")
    status = str(status).split(":")[-1]
    applications = await sync_to_async(list)(
        ProcessingApplication.objects.select_related("user").filter(
            status=status,
            city_id=data.get("city_id"),
            invited_date=data.get("appointment_date"),
            user=user,
        )
    )
    return applications


async def get_applies_by_vacancy(vacancy: Vacancy, partner: Partner = None):
    status = ApplicationStatus.CLOSED
    applications = await sync_to_async(list)(
        ProcessingApplication.objects.select_related("user").filter(
            vacancy_id=vacancy.id,
            status=status,
            partner=partner,
        )
    )
    return applications


async def get_vacancy(
    user: TelegramUser, state: FSMContext, partner: Partner = None
) -> Vacancy:
    data = await state.get_data()
    vacancy_id = data.get("vacancy_id")
    city_id = data.get("city_id")
    vacancy = await database_sync_to_async(Vacancy.objects.get)(id=vacancy_id)
    city = await database_sync_to_async(City.objects.get)(id=city_id)
    return vacancy, city


async def count_applies_from_referral(user: TelegramUser, partner: Partner) -> int:
    count = await sync_to_async(
        lambda: ProcessingApplication.objects.filter(
            user=user, user__is_partner=True
        ).count()
    )()
    return count
