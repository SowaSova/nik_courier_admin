from aiogram import Dispatcher

from .calendar import router as calendar_router
from .city_choice import router as city_choice_router
# from .control import router as control_router
from .create_apply import router as create_apply_router
from .data_appointment import router as appointment_router
from .data_car import router as car_router
from .data_documents import router as documents_router
from .data_full_name import router as full_name_router
from .data_phone_number import router as phone_number_router
from .data_tax_status import router as tax_status_router
from .data_vacancy import router as data_vacancy_router
from .pagination import router as pagination_router
from .personal_cabinet import router as personal_cabinet_router
from .referral import router as referral_router
from .start import router as start_router
from .status_choice import router as status_choice_router
from .training import router as training_router


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        start_router,
        pagination_router,
        city_choice_router,
        calendar_router,
        full_name_router,
        phone_number_router,
        tax_status_router,
        car_router,
        documents_router,
        appointment_router,
        personal_cabinet_router,
        status_choice_router,
        referral_router,
        create_apply_router,
        data_vacancy_router,
        training_router,
        # control_router,
    )
