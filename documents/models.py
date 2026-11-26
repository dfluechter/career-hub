from pathlib import Path

from django.core.validators import FileExtensionValidator
from django.db import models


class DocumentType(models.TextChoices):
    CV = "cv", "Lebenslauf"
    COVER_LETTER = "cover_letter", "Anschreiben"


class Document(models.Model):
    title = models.CharField(
        "Bezeichnung",
        max_length=255,
    )

    document_type = models.CharField(
        "Dokumenttyp",
        max_length=20,
        choices=DocumentType.choices,
        db_index=True,
    )

    file = models.FileField(
        "Datei",
        upload_to="documents/%Y/%m/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["docx"]
            )
        ],
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
            "document_type",
            "-updated_at",
        ]
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"

    @property
    def filename(self) -> str:
        return Path(self.file.name).name

    def __str__(self) -> str:
        return self.title