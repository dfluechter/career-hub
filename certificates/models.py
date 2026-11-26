from pathlib import Path

from django.core.validators import FileExtensionValidator
from django.db import models


class CertificateCategory(models.TextChoices):
    SOFTWARE_DEVELOPMENT = (
        "software_development",
        "Softwareentwicklung",
    )

    DATA_ANALYSIS = (
        "data_analysis",
        "Datenanalyse",
    )

    SOFTWARE_TESTING = (
        "software_testing",
        "Software Testing",
    )

    IT_SUPPORT = (
        "it_support",
        "IT-Support",
    )

    CLOUD_DEVOPS = (
        "cloud_devops",
        "Cloud & DevOps",
    )

    AI = (
        "ai",
        "Künstliche Intelligenz",
    )

    OTHER = (
        "other",
        "Sonstige",
    )


class Certificate(models.Model):
    title = models.CharField(
        "Zertifikatsname",
        max_length=255,
    )

    issuer = models.CharField(
        "Anbieter",
        max_length=255,
    )

    category = models.CharField(
        "Kategorie",
        max_length=30,
        choices=CertificateCategory.choices,
        default=CertificateCategory.OTHER,
        db_index=True,
    )

    file = models.FileField(
        "PDF-Datei",
        upload_to="certificates/%Y/%m/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"],
            )
        ],
    )

    issued_at = models.DateField(
        "Ausgestellt am",
        null=True,
        blank=True,
    )

    expires_at = models.DateField(
        "Gültig bis",
        null=True,
        blank=True,
    )

    credential_id = models.CharField(
        "Credential-ID",
        max_length=255,
        blank=True,
    )

    credential_url = models.URLField(
        "Credential-URL",
        max_length=1000,
        blank=True,
    )

    description = models.TextField(
        "Beschreibung",
        blank=True,
    )

    active = models.BooleanField(
        "Aktiv",
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        "Erstellt am",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "Aktualisiert am",
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-issued_at",
            "title",
        ]

        verbose_name = "Zertifikat"
        verbose_name_plural = "Zertifikate"

    @property
    def filename(self) -> str:
        return Path(
            self.file.name
        ).name

    def __str__(self) -> str:
        return (
            f"{self.title} – {self.issuer}"
        )