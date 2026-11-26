from django.db import models
from documents.models import Document
from jobs.models import JobOffer


class ApplicationStatus(models.TextChoices):
    PREPARING = "preparing", "In Vorbereitung"
    READY = "ready", "Bereit"
    SUBMITTED = "submitted", "Beworben"
    INTERVIEW = "interview", "Vorstellungsgespräch"
    REJECTED = "rejected", "Absage"
    ACCEPTED = "accepted", "Zusage"


class Application(models.Model):
    cv = models.ForeignKey(
        Document,
        verbose_name="Lebenslauf",
        related_name="cv_applications",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={
            "document_type": "cv",
            "active": True,
        },
    )

    cover_letter = models.ForeignKey(
        Document,
        verbose_name="Anschreiben",
        related_name="cover_letter_applications",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={
            "document_type": "cover_letter",
            "active": True,
        },
    )
    job = models.OneToOneField(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="application",
        verbose_name="Stellenangebot",
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PREPARING,
        db_index=True,
    )

    notes = models.TextField(
        "Notizen",
        blank=True,
    )

    submitted_at = models.DateTimeField(
        "Beworben am",
        null=True,
        blank=True,
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
        ordering = ["-created_at"]
        verbose_name = "Bewerbung"
        verbose_name_plural = "Bewerbungen"

    def __str__(self) -> str:
        return f"Bewerbung: {self.job}"