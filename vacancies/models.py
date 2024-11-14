from django.db import models

from geo.models import City


class Vacancy(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название вакансии")
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name="vacancies",
        verbose_name="Город",
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        unique_together = ("name", "city")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city})"
