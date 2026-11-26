from dataclasses import dataclass

from django.db import IntegrityError, transaction

from jobs.models import JobOffer, JobStatus

from .parser import ParsedJobEmail, parse_email_bytes


@dataclass(frozen=True, slots=True)
class ImportResult:
    job: JobOffer
    created: bool


def normalize_message_id(
    message_id: str,
) -> str:
    """
    Normalisiert die Message-ID für die Duplikaterkennung.

    Führende und abschließende Leerzeichen werden entfernt.
    Die Groß-/Kleinschreibung wird vereinheitlicht.
    """

    normalized = message_id.strip().casefold()

    if not normalized:
        raise ValueError(
            "Die Message-ID darf nicht leer sein."
        )

    return normalized


@transaction.atomic
def import_parsed_job(
    parsed: ParsedJobEmail,
    *,
    source: str = "email",
) -> ImportResult:
    source_message_id = normalize_message_id(
        parsed.message_id,
    )

    defaults = {
        "title": parsed.title,
        "company": parsed.company,
        "location": parsed.location,
        "category": parsed.category,
        "status": JobStatus.NEW,
        "source": source,
        "source_mailbox": parsed.mailbox,
        "job_url": parsed.job_url,
        "received_at": parsed.received_at,
    }

    try:
        with transaction.atomic():
            job, created = JobOffer.objects.get_or_create(
                source_message_id=source_message_id,
                defaults=defaults,
            )

    except IntegrityError:
        job = JobOffer.objects.get(
            source_message_id=source_message_id,
        )

        created = False

    return ImportResult(
        job=job,
        created=created,
    )


def import_email_bytes(
    raw_message: bytes,
    *,
    mailbox: str,
    source: str = "email",
) -> ImportResult:
    """
    Kombiniert Parser und Datenbankimport.
    """

    parsed = parse_email_bytes(
        raw_message,
        mailbox=mailbox,
    )

    return import_parsed_job(
        parsed,
        source=source,
    )