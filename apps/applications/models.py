from django.db import models

from adminpanel.constants import (
    ApplicationStatus,
    CarTonnage,
    DocumentType,
    ProcessingApplicationType,
    TaxStatus,
)
from apps.geo.models import City
from apps.users.models import TelegramUser
from apps.vacancies.models import Vacancy


class Application(models.Model):
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.status


class ProcessingApplication(Application):
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="processing_application",
        verbose_name="Пользователь Telegram",
    )
    partner = models.ForeignKey(
        "users.Partner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Партнер",
    )
    bitrix_lead_id = models.CharField(max_length=255, blank=True, null=True)
    is_finalized = models.BooleanField(default=False, verbose_name="Финализирована")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=30, verbose_name="Номер телефона")
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, verbose_name="Город"
    )
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.SET_NULL, null=True, verbose_name="Вакансия"
    )
    car_tonnage = models.CharField(
        max_length=20,
        choices=CarTonnage.choices,
        verbose_name="Грузоподъемность",
        null=True,
        blank=True,
    )
    tax_status = models.CharField(
        max_length=20,
        choices=TaxStatus.choices,
        verbose_name="Статус налогоплательщика",
        null=True,
        blank=True,
    )
    source = models.CharField(
        max_length=20,
        choices=ProcessingApplicationType.choices,
        default=ProcessingApplicationType.FUNNEL_AGENCY,
        verbose_name="Источник",
    )
    invited_date = models.DateField(
        null=True, blank=True, verbose_name="Дата приглашения"
    )
    reward_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма вознаграждения",
        default=1000,
    )

    class Meta:
        verbose_name = "Заявка на обработку"
        verbose_name_plural = "Заявки на обработку"

    def __str__(self):
        return self.full_name


class PaymentApplication(Application):
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    payment_method = models.CharField(max_length=50, verbose_name="Способ оплаты")
    recipient_details = models.TextField(verbose_name="Детали получателя")

    class Meta:
        verbose_name = "Заявка на оплату"
        verbose_name_plural = "Заявки на оплату"

    def __str__(self):
        return f"Платеж #{self.pk} на сумму {self.amount} от {self.user}"


class Document(models.Model):
    application = models.ForeignKey(
        ProcessingApplication,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Заявка",
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        verbose_name="Тип документа",
    )
    file = models.FileField(upload_to="documents/", verbose_name="Файл документа")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return f"{self.document_type} для заявки #{self.application.pk}"
