# Generated by Django 5.1.3 on 2024-11-26 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_partner_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partner",
            name="proccess_type",
            field=models.CharField(
                choices=[
                    ("funnel_agency", "Агент"),
                    ("funnel_cpa", "CPA"),
                    ("referral", "Реферальная"),
                ],
                max_length=255,
                verbose_name="Тип воронки",
            ),
        ),
    ]
