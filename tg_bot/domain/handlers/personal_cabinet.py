from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async

from adminpanel.constants import ApplicationStatus
from applications.models import ProcessingApplication
from tg_bot.domain.keyboards import send_status_choice_keyboard
from tg_bot.domain.states import PersonalCabinetForm
from users.models import Partner, TelegramUser

router = Router()


@router.callback_query(F.data == "personal_cabinet")
async def process_personal_cabinet(
    callback_query: CallbackQuery, state: PersonalCabinetForm, user: TelegramUser
):
    partner = await sync_to_async(Partner.objects.get)(telegram_id=user.telegram_id)
    count = await sync_to_async(
        lambda: ProcessingApplication.objects.filter(
            user__invited_by=partner, status=ApplicationStatus.ACTIVE
        ).count()
    )()
    full_name = f"{html.bold('ФИО: ')} {partner.name}.\n"
    applications_count = f"{html.bold('Кол-во заявок(В работе): ')} {count}.\n"
    balance = f"{html.bold('Баланс: ')} {partner.balance}.\n"
    text = full_name + applications_count + balance
    await callback_query.message.answer(
        text=text, reply_markup=send_status_choice_keyboard()
    )
    await state.set_state(PersonalCabinetForm.WaitingForStatusChoice)
    await callback_query.answer()
