from django.contrib import admin

from .models import BroadcastMessage


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    pass
