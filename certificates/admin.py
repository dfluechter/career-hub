from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "issuer",
        "category",
        "issued_at",
        "active",
    )

    list_filter = (
        "category",
        "active",
        "issuer",
    )

    search_fields = (
        "title",
        "issuer",
        "credential_id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )