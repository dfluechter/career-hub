from datetime import datetime, timezone
from email.message import EmailMessage

from django.test import TestCase

from jobs.models import (
    JobCategory,
    JobOffer,
    JobStatus,
)
from mail_import.services.importer import (
    import_email_bytes,
    import_parsed_job,
    normalize_message_id,
)
from mail_import.services.parser import ParsedJobEmail


def build_parsed_job(
    *,
    message_id: str = "<job-001@example.com>",
) -> ParsedJobEmail:
    return ParsedJobEmail(
        message_id=message_id,
        mailbox="dominik@example.com",
        sender="jobs@example.com",
        subject="Stellenangebot: Python Developer",
        title="Python Developer",
        company="Beispiel GmbH",
        location="Lippstadt",
        body="Django, PostgreSQL und Python",
        job_url="https://jobs.example.com/python",
        received_at=datetime(
            2026,
            10,
            28,
            8,
            0,
            tzinfo=timezone.utc,
        ),
        category=JobCategory.SOFTWARE_DEVELOPER,
    )


def build_email() -> bytes:
    message = EmailMessage()

    message["Subject"] = (
        "Stellenangebot: Python Developer"
    )
    message["From"] = "jobs@example.com"
    message["To"] = "dominik@example.com"
    message["Message-ID"] = (
        "<email-import-001@example.com>"
    )
    message["Date"] = (
        "Wed, 28 Oct 2026 08:00:00 +0100"
    )

    message.set_content(
        "Stellenbezeichnung: Python Developer\n"
        "Unternehmen: Beispiel GmbH\n"
        "Standort: Lippstadt\n"
        "https://jobs.example.com/python"
    )

    return message.as_bytes()


class MessageIdNormalizationTests(TestCase):
    def test_message_id_is_normalized(self):
        result = normalize_message_id(
            "  <JOB-001@EXAMPLE.COM>  "
        )

        self.assertEqual(
            result,
            "<job-001@example.com>",
        )

    def test_empty_message_id_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "Die Message-ID darf nicht leer sein.",
        ):
            normalize_message_id("   ")


class JobImporterTests(TestCase):
    def test_parsed_job_creates_job_offer(self):
        result = import_parsed_job(
            build_parsed_job(),
            source="test-email",
        )

        self.assertTrue(
            result.created,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

        job = result.job

        self.assertEqual(
            job.title,
            "Python Developer",
        )

        self.assertEqual(
            job.company,
            "Beispiel GmbH",
        )

        self.assertEqual(
            job.location,
            "Lippstadt",
        )

        self.assertEqual(
            job.category,
            JobCategory.SOFTWARE_DEVELOPER,
        )

        self.assertEqual(
            job.status,
            JobStatus.NEW,
        )

        self.assertEqual(
            job.source,
            "test-email",
        )

        self.assertEqual(
            job.source_message_id,
            "<job-001@example.com>",
        )

    def test_same_message_is_not_imported_twice(self):
        parsed = build_parsed_job()

        first = import_parsed_job(
            parsed,
        )

        second = import_parsed_job(
            parsed,
        )

        self.assertTrue(
            first.created,
        )

        self.assertFalse(
            second.created,
        )

        self.assertEqual(
            first.job.pk,
            second.job.pk,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

    def test_message_id_comparison_is_case_insensitive(self):
        first = import_parsed_job(
            build_parsed_job(
                message_id="<JOB-001@EXAMPLE.COM>",
            )
        )

        second = import_parsed_job(
            build_parsed_job(
                message_id="<job-001@example.com>",
            )
        )

        self.assertTrue(
            first.created,
        )

        self.assertFalse(
            second.created,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

    def test_existing_job_is_not_overwritten(self):
        original = import_parsed_job(
            build_parsed_job(),
        )

        changed = build_parsed_job()

        changed = ParsedJobEmail(
            message_id=changed.message_id,
            mailbox=changed.mailbox,
            sender=changed.sender,
            subject=changed.subject,
            title="Manipulierter Titel",
            company=changed.company,
            location=changed.location,
            body=changed.body,
            job_url=changed.job_url,
            received_at=changed.received_at,
            category=changed.category,
        )

        duplicate = import_parsed_job(
            changed,
        )

        original.job.refresh_from_db()

        self.assertFalse(
            duplicate.created,
        )

        self.assertEqual(
            original.job.title,
            "Python Developer",
        )

    def test_raw_email_can_be_parsed_and_imported(self):
        result = import_email_bytes(
            build_email(),
            mailbox="dominik@example.com",
            source="test-provider",
        )

        self.assertTrue(
            result.created,
        )

        job = result.job

        self.assertEqual(
            job.title,
            "Python Developer",
        )

        self.assertEqual(
            job.source,
            "test-provider",
        )

        self.assertEqual(
            job.source_mailbox,
            "dominik@example.com",
        )

        self.assertEqual(
            job.job_url,
            "https://jobs.example.com/python",
        )