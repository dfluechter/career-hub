from django.db import models


class JobCategory(models.TextChoices):
    IT_TECHNICIAN = "it_technician", "IT-Techniker"
    SOFTWARE_DEVELOPER = "software_developer", "Software Entwickler"
    DATA_ANALYST = "data_analyst", "Data Analyst"
    SOFTWARE_TESTER = "software_tester", "Software Tester"
    OTHER = "other", "Sonstige"


class JobStatus(models.TextChoices):
    NEW = "new", "Neu"
    SAVED = "saved", "Gemerkt"
    PREPARING = "preparing", "Bewerbung vorbereiten"
    APPLIED = "applied", "Beworben"
    INTERVIEW = "interview", "Vorstellungsgespräch"
    REJECTED = "rejected", "Absage"
    ACCEPTED = "accepted", "Zusage"


class JobOffer(models.Model):
    title = models.CharField(
        "Stellenbezeichnung",
        max_length=255,
    )

    company = models.CharField(
        "Unternehmen",
        max_length=255,
        blank=True,
    )

    location = models.CharField(
        "Standort",
        max_length=255,
        blank=True,
    )

    category = models.CharField(
        "Kategorie",
        max_length=30,
        choices=JobCategory.choices,
        default=JobCategory.OTHER,
        db_index=True,
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.NEW,
        db_index=True,
    )

    source = models.CharField(
        "Quelle",
        max_length=100,
        blank=True,
    )

    source_mailbox = models.EmailField(
        "E-Mail-Postfach",
    )

    source_message_id = models.CharField(
        "E-Mail-ID",
        max_length=255,
        unique=True,
    )

    job_url = models.URLField(
        "Stellenanzeige",
        max_length=1000,
        blank=True,
    )

    received_at = models.DateTimeField(
        "Eingegangen am",
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
        ordering = ["-received_at"]
        verbose_name = "Stellenangebot"
        verbose_name_plural = "Stellenangebote"

    def __str__(self) -> str:
        if self.company:
            return f"{self.title} – {self.company}"

        return self.title