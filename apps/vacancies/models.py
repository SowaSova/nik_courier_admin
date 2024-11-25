from django.db import models

from apps.geo.models import City


class Vacancy(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название вакансии"
    )
    conditions = models.TextField(verbose_name="Условия", null=True, blank=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"
