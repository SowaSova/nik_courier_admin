from django.db import models


class City(models.Model):
    btx_id = models.BigIntegerField(
        verbose_name="ID города в Битриксе", null=True, unique=True, blank=True
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Название города")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ["name"]

    def __str__(self):
        return self.name
