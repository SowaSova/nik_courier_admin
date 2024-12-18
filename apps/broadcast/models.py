from django.db import models


class BroadcastMessage(models.Model):
    message_text = models.TextField(verbose_name="Текст сообщения")
    attachments = models.FileField(upload_to="attachments/", null=True, blank=True)
    city = models.ForeignKey(
        "geo.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Город",
        help_text="Пустое поле - рассылка по всем городам",
    )
    scheduled_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Время отправки"
    )
    is_sent = models.BooleanField(default=False, verbose_name="Отправлено")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сообщение для рассылки"
        verbose_name_plural = "Сообщения для рассылки"

    def __str__(self):
        return f"Рассылка от {self.created_at}"
