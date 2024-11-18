# Generated by Django 5.1.3 on 2024-11-18 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("geo", "0001_initial"),
        ("users", "0001_initial"),
        ("vacancies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Новая заявка"),
                            ("active", "В работе"),
                            ("closed", "Завершена"),
                        ],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Дата последнего изменения"
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Сумма"
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(max_length=50, verbose_name="Способ оплаты"),
                ),
                (
                    "recipient_details",
                    models.TextField(verbose_name="Детали получателя"),
                ),
            ],
            options={
                "verbose_name": "Заявка на оплату",
                "verbose_name_plural": "Заявки на оплату",
            },
        ),
        migrations.CreateModel(
            name="ProcessingApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Новая заявка"),
                            ("active", "В работе"),
                            ("closed", "Завершена"),
                        ],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Дата последнего изменения"
                    ),
                ),
                ("full_name", models.CharField(max_length=255, verbose_name="ФИО")),
                (
                    "phone_number",
                    models.CharField(max_length=30, verbose_name="Номер телефона"),
                ),
                (
                    "car_tonnage",
                    models.CharField(
                        choices=[
                            ("0.5", "до 0.5 т"),
                            ("1", "до 1 т"),
                            ("1.5", "до 1.5 т"),
                            ("1.5+", "от 1.5 т"),
                            ("Нет", "Нет машины (нужна аренда)"),
                        ],
                        default="0.5",
                        max_length=20,
                        verbose_name="Грузоподъемность",
                    ),
                ),
                (
                    "tax_status",
                    models.CharField(
                        choices=[
                            ("СМЗ", "Самозанятый"),
                            ("ИП", "Индивидуальный предприниматель"),
                            ("Физ", "Физическое лицо"),
                        ],
                        default="СМЗ",
                        max_length=20,
                        verbose_name="Статус налогоплательщика",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("funnel_agency", "Воронка 1 (агент)"),
                            ("funnel_cpa", "Воронка 2 (CPA)"),
                            ("referral", "Реферальная"),
                        ],
                        default="funnel_agency",
                        max_length=20,
                        verbose_name="Источник",
                    ),
                ),
                (
                    "invited_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата приглашения"
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="geo.city",
                        verbose_name="Город",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processing_application",
                        to="users.telegramuser",
                        verbose_name="Пользователь Telegram",
                    ),
                ),
                (
                    "vacancy",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="vacancies.vacancy",
                        verbose_name="Вакансия",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка на обработку",
                "verbose_name_plural": "Заявки на обработку",
            },
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("license", "Фото прав"),
                            ("passport", "Паспорт"),
                            ("registration", "Регистрация"),
                            ("tax_document", "Налоговый документ"),
                            ("other", "Прочие документы"),
                        ],
                        max_length=20,
                        verbose_name="Тип документа",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="documents/", verbose_name="Файл документа"
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата загрузки"
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="applications.processingapplication",
                        verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ",
                "verbose_name_plural": "Документы",
            },
        ),
    ]
