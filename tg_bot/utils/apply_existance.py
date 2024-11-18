from asgiref.sync import sync_to_async

from applications.models import ProcessingApplication
from users.models import TelegramUser


async def application_exists(user: TelegramUser) -> bool:
    res = await sync_to_async(ProcessingApplication.objects.filter)(user=user)
    return await res.aexists()
