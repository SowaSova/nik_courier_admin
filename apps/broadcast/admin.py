from django.contrib import admin

from .models import BroadcastMessage


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ["message_text", "created_at", "is_sent"]
