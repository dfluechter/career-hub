from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "status",
        "submitted_at",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "job__title",
        "job__company",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fields = (
        "job",
        "status",
        "cv",
        "cover_letter",
        "notes",
        "submitted_at",
        "created_at",
        "updated_at",
    )