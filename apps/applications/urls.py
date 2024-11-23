from django.urls import path

from apps.applications import views

urlpatterns = [
    path("bitrix-webhook/", views.bitrix_webhook, name="bitrix_webhook"),
]
