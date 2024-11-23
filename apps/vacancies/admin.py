from django.contrib import admin

from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ["name", "city"]
    search_fields = ["name", "city"]
    list_filter = ["city"]
