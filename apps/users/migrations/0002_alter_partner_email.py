# Generated by Django 5.1.3 on 2024-11-26 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partner",
            name="email",
            field=models.EmailField(
                blank=True, max_length=255, null=True, verbose_name="Email"
            ),
        ),
    ]
