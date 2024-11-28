from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Partner, TelegramChannel, TelegramUser


@admin.register(TelegramChannel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "chat_id"]


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "telegram_id",
        "tg_username",
        "created_at",
        "is_partner",
        "is_verified",
    ]
    search_fields = ["telegram_id"]
    list_filter = ["created_at", "is_partner"]


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone_number",
        "email",
        "active_link",
    ]
    search_fields = [
        "name",
        "phone_number",
        "email",
    ]
    list_filter = ["created_at"]
    readonly_fields = [
        "created_at",
        "referal_idx",
        "btx_id",
    ]
    ordering = ["-created_at"]
    show_facets = admin.ShowFacets.ALWAYS

    def active_link(self, obj):
        from django.conf import settings

        url = f"https://t.me/{settings.BOT_NAME}?start={obj.referal_idx}"
        return mark_safe(f"<a href='{url}' target='_blank'>{url}</a>")

    active_link.short_description = "Реферальная ссылка"
