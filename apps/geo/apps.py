from django.apps import AppConfig


class GeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.geo"
    verbose_name = "Город"
    verbose_name_plural = "Города"
