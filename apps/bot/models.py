from django.db import models

from adminpanel.constants import ButtonType, MediaType


class BotMessage(models.Model):
    identifier = models.ForeignKey(
        "BotMessageType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name="Тип сообщения",
    )
    text = models.TextField(verbose_name="Текст сообщения")
    media = models.ForeignKey(
        "BotMedia",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name="Медиа",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Сообщение бота"
        verbose_name_plural = "Сообщения бота"

    def __str__(self):
        return self.identifier.name


class BotMessageType(models.Model):
    name = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Название типа",
        help_text="Например: 'start'",
    )
    description = models.TextField(verbose_name="Описание", null=True, blank=True)

    class Meta:
        verbose_name = "Тип сообщения бота"
        verbose_name_plural = "Типы сообщений бота"

    def __str__(self):
        return self.name


class BotButton(models.Model):
    message = models.ForeignKey(
        BotMessage,
        on_delete=models.CASCADE,
        related_name="buttons",
        verbose_name="Сообщение",
    )
    text = models.CharField(max_length=100, verbose_name="Текст кнопки")
    button_type = models.CharField(
        max_length=20,
        choices=ButtonType.choices,
        default=ButtonType.TEXT,
        verbose_name="Тип кнопки",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активность кнопки")
    payload = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Полезная нагрузка"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Кнопка бота"
        verbose_name_plural = "Кнопки бота"
        ordering = ["order"]

    def __str__(self):
        return f"{self.text} ({self.get_button_type_display()})"


class BotMedia(models.Model):
    # message = models.ForeignKey(
    #     BotMessage,
    #     on_delete=models.CASCADE,
    #     related_name="media",
    #     verbose_name="Сообщение",
    #     null=True,
    #     blank=True,
    # )
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.PHOTO,
        verbose_name="Тип медиа",
    )
    file = models.FileField(upload_to="bot_media/", verbose_name="Файл")
    description = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Описание"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Медиа бота"
        verbose_name_plural = "Медиа бота"

    def __str__(self):
        return f"{self.get_media_type_display()} - {self.file.name}"
