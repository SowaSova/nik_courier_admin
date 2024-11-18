from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from applications.models import ProcessingApplication
from users.models import Partner, TelegramUser


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


async def count_applies_from_referral(user: TelegramUser, partner: Partner) -> int:
    count = await sync_to_async(
        lambda: ProcessingApplication.objects.filter(
            user=user, user__is_partner=True
        ).count()
    )()
    return count
