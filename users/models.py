from django.db import models

from adminpanel.constants import ProcessingApplicationType


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="ID Telegram", null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "TG-Пользователь"
        verbose_name_plural = "TG-Пользователи"


class Partner(TelegramUser):
    name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(
        max_length=255, verbose_name="Номер телефона"
    )
    email = models.EmailField(max_length=255, verbose_name="Email")
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Баланс", default=0
    )
    proccess_type = models.CharField(
        max_length=255,
        choices=ProcessingApplicationType.choices,
        default=ProcessingApplicationType.FUNNEL_AGENCY,
        verbose_name="Тип воронки",
    )
    referal_idx = models.CharField(
        max_length=20, verbose_name="Реферальный индекс", unique=True
    )

    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        import secrets

        from adminpanel.constants import BOT_NAME

        super().save(*args, **kwargs)
        if not self.referal_idx:
            self.referal_idx = secrets.token_urlsafe(10)
        super().save(*args, **kwargs)
