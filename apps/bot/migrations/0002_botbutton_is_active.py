# Generated by Django 5.1.3 on 2024-11-28 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="botbutton",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активность кнопки"),
        ),
    ]
