import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adminpanel.settings")

app = Celery("adminpanel")

# Используйте строку для брокера Redis
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND


# Настройки временной зоны и т.д.
app.conf.timezone = settings.TIME_ZONE

# Автоматическое обнаружение задач в ваших приложениях
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "send-scheduled-messages-every-minute": {
        "task": "tg_bot.tasks.send_scheduled_messages",
        "schedule": timedelta(minutes=1),
    },
}
