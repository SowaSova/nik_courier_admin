from django.contrib import admin
from django.urls import path

from adminpanel.settings import get_app_list

admin.AdminSite.get_app_list = get_app_list

urlpatterns = [
    path("admin/", admin.site.urls),
]
