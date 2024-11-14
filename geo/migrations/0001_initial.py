# Generated by Django 5.1.3 on 2024-11-14 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Название города"
                    ),
                ),
            ],
            options={
                "verbose_name": "Город",
                "verbose_name_plural": "Города",
                "ordering": ["name"],
            },
        ),
    ]
