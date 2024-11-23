import copy
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = Path(__file__).parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG")


ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "apps.users.apps.UsersConfig",
    "apps.broadcast.apps.BroadcastConfig",
    "apps.applications.apps.ApplicationsConfig",
    "apps.vacancies.apps.VacanciesConfig",
    "apps.geo.apps.GeoConfig",
    "apps.bot.apps.BotConfig",
    "tg_bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "adminpanel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "adminpanel.wsgi.application"
ASGI_APPLICATION = "adminpanel.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PWD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CELERY

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_POOL_LIMIT = None

# TG BOT

BOT_NAME = os.getenv("BOT_NAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# BITRIX

BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL")
BITRIX_WH_CRM = os.getenv("BITRIX_WH_CRM")
BITRIX_WH_FILES = os.getenv("BITRIX_WH_FILES")
BITRIX_FOLDER_ID = os.getenv("BITRIX_FOLDER_ID")
BITRIX_WEBHOOK_TOKEN = os.getenv("BITRIX_WEBHOOK_TOKEN")

# ADMIN REORDER

ADMIN_ORDERING = [
    ("users", ["TelegramUser", "Partner"]),
    ("applications", ["ProcessingApplication", "PaymentApplication"]),
    ("broadcast", ["Broadcast"]),
]


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)

    app_dict_copy = copy.deepcopy(app_dict)
    for app_label, object_list in ADMIN_ORDERING:
        app = app_dict_copy.pop(app_label)
        object_dict = {value: idx for idx, value in enumerate(object_list)}
        app["models"].sort(
            key=lambda x: object_dict.get(x["object_name"], len(object_list) + 1)
        )
        yield app

    app_list = sorted(app_dict_copy.values(), key=lambda x: x["name"].lower())
    for app in app_list:
        app["models"].sort(key=lambda x: x["name"])
        yield app
