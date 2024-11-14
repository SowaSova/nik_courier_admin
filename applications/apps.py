from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications"
    verbose_name = "Заявка"
    verbose_name_plural = "Заявки"
