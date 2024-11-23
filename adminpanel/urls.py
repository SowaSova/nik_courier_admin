from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from adminpanel import settings
from adminpanel.settings import get_app_list

admin.AdminSite.get_app_list = get_app_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ws/", include("apps.applications.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
