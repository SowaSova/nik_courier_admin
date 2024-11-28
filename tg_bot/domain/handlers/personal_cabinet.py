from typing import List, Optional

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from adminpanel.constants import ApplicationStatus
from apps.applications.models import ProcessingApplication
from apps.bot.models import BotButton, BotMedia
from apps.users.models import Partner, TelegramUser
from tg_bot.domain.keyboards import send_status_choice_keyboard
from tg_bot.domain.states import PersonalCabinetForm
from tg_bot.utils.bot_config import with_bot_message

router = Router()


@router.callback_query(F.data == "personal_cabinet")
@with_bot_message("personal_cabinet")
async def process_personal_cabinet(
    callback_query: CallbackQuery,
    state: PersonalCabinetForm,
    user: TelegramUser,
    bot_message_text: Optional[str],
    media: Optional[BotMedia],
    buttons: List[BotButton],
):
    partner = await sync_to_async(Partner.objects.get)(user=user)
    count = await sync_to_async(
        lambda: ProcessingApplication.objects.filter(
            user=user, status=ApplicationStatus.ACTIVE, user__is_partner=True
        ).count()
    )()
    if not bot_message_text:
        bot_message_text = (
            "<b>ФИО:</b> {partner_name}.\n"
            "<b>Кол-во заявок(В работе):</b> {applications_count}.\n"
            "<b>Баланс:</b> {balance}"
        )
    text = bot_message_text.format(
        partner_name=partner.name, applications_count=count, balance=partner.balance
    )

    await callback_query.message.answer(
        text=text, reply_markup=send_status_choice_keyboard()
    )
    await state.set_state(PersonalCabinetForm.WaitingForStatusChoice)
    await callback_query.answer()
