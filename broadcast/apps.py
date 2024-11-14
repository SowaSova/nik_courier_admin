from django.apps import AppConfig


class BroadcastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "broadcast"
    verbose_name = "Рассылка"
    verbose_name_plural = "Рассылки"
