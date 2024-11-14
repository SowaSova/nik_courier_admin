from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Partner, TelegramUser


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "created_at"]
    search_fields = ["telegram_id"]


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        # "telegram_id",
        "phone_number",
        "email",
        "active_link",
    ]
    search_fields = [
        "telegram_id",
        "name",
        "phone_number",
        "email",
    ]
    list_filter = ["created_at"]
    readonly_fields = [
        "created_at",
        "telegram_id",
        "referal_idx",
    ]
    ordering = ["-created_at"]
    show_facets = admin.ShowFacets.ALWAYS

    def active_link(self, obj):
        from adminpanel.constants import BOT_NAME

        url = f"https://t.me/{BOT_NAME}?start={obj.referal_idx}"
        return mark_safe(f"<a href='{url}' target='_blank'>{url}</a>")

    active_link.short_description = "Реферальная ссылка"
