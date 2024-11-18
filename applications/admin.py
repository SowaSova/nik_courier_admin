from django.contrib import admin

from .models import Document, PaymentApplication, ProcessingApplication


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1


@admin.register(PaymentApplication)
class PaymentApplicationAdmin(admin.ModelAdmin):
    pass


@admin.register(ProcessingApplication)
class ProcessingApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "status",
        "phone_number",
        "city",
        "vacancy",
        "source",
        "invited_date",
    ]
    search_fields = ["full_name", "phone_number", "invited_date"]
    readonly_fields = ["created_at"]
    list_filter = ["city", "source", "invited_date"]
    inlines = [DocumentInline]
    show_facets = admin.ShowFacets.ALWAYS
