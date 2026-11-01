from django.contrib import admin

from .models import JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "category",
        "status",
        "source_mailbox",
        "received_at",
    )

    list_filter = (
        "category",
        "status",
        "source_mailbox",
        "source",
    )

    search_fields = (
        "title",
        "company",
        "location",
    )

    ordering = (
        "-received_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )