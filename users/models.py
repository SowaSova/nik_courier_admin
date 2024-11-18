from django.db import models

from adminpanel.constants import ProcessingApplicationType


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="ID Telegram", null=True, blank=True
    )
    tg_username = models.CharField(
        max_length=255, verbose_name="TG Username", null=True, blank=True
    )
    invited_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пригласил",
        related_name="referrals",
    )
    is_partner = models.BooleanField(default=False, verbose_name="Партнёр")
    is_verified = models.BooleanField(default=False, verbose_name="Подтверждён")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "TG-Пользователь"
        verbose_name_plural = "TG-Пользователи"

    def __str__(self):
        return self.tg_username or self.telegram_id or str(self.created_at)

    def save(self, *args, **kwargs):
        tg_url = "https://t.me/"
        if self.tg_username and self.tg_username.startswith("@"):
            self.tg_username = self.tg_username[1:]  # удаляем @
        if self.tg_username and self.tg_username.startswith(tg_url):
            self.tg_username = self.tg_username[len(tg_url) :]
        super().save(*args, **kwargs)


class Partner(TelegramUser):
    name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=255, verbose_name="Номер телефона")
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

        if not self.referal_idx:
            self.referal_idx = secrets.token_urlsafe(10)
        self.is_partner = True
        super().save(*args, **kwargs)
