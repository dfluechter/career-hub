from email.message import EmailMessage

from django.test import SimpleTestCase

from jobs.models import JobCategory
from mail_import.services.parser import parse_email_bytes


def build_email(
    *,
    subject: str = "Stellenangebot: Python Developer",
    message_id: str = "<job-001@example.com>",
    body: str = (
        "Stellenbezeichnung: Python Developer\n"
        "Unternehmen: Beispiel GmbH\n"
        "Standort: Lippstadt\n"
        "Mehr Informationen: "
        "https://jobs.example.com/python-developer"
    ),
) -> bytes:
    """
    Erstellt eine kontrollierte Test-E-Mail.
    """

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = "jobs@example.com"
    message["To"] = "dominik@example.com"
    message["Date"] = (
        "Wed, 28 Oct 2026 08:00:00 +0100"
    )

    if message_id:
        message["Message-ID"] = message_id

    message.set_content(body)

    return message.as_bytes()


class MailParserTests(SimpleTestCase):
    def test_plain_text_email_is_parsed(self):
        parsed = parse_email_bytes(
            build_email(),
            mailbox="dominik@example.com",
        )

        self.assertEqual(
            parsed.message_id,
            "<job-001@example.com>",
        )

        self.assertEqual(
            parsed.mailbox,
            "dominik@example.com",
        )

        self.assertEqual(
            parsed.sender,
            "jobs@example.com",
        )

        self.assertEqual(
            parsed.subject,
            "Stellenangebot: Python Developer",
        )

        self.assertEqual(
            parsed.title,
            "Python Developer",
        )

        self.assertEqual(
            parsed.company,
            "Beispiel GmbH",
        )

        self.assertEqual(
            parsed.location,
            "Lippstadt",
        )

        self.assertEqual(
            parsed.job_url,
            "https://jobs.example.com/python-developer",
        )

        self.assertEqual(
            parsed.category,
            JobCategory.SOFTWARE_DEVELOPER,
        )

        self.assertEqual(
            parsed.received_at.isoformat(),
            "2026-10-28T08:00:00+01:00",
        )

    def test_subject_is_used_as_title_fallback(self):
        parsed = parse_email_bytes(
            build_email(
                subject="Jobangebot: Django Developer",
                body=(
                    "Unternehmen: Beispiel GmbH\n"
                    "Standort: Lippstadt"
                ),
            ),
            mailbox="dominik@example.com",
        )

        self.assertEqual(
            parsed.title,
            "Django Developer",
        )

        self.assertEqual(
            parsed.company,
            "Beispiel GmbH",
        )

        self.assertEqual(
            parsed.location,
            "Lippstadt",
        )

        self.assertEqual(
            parsed.category,
            JobCategory.SOFTWARE_DEVELOPER,
        )

    def test_missing_message_id_is_rejected(self):
        raw_message = build_email(
            message_id="",
        )

        with self.assertRaisesMessage(
            ValueError,
            "Die E-Mail enthält keine Message-ID.",
        ):
            parse_email_bytes(
                raw_message,
                mailbox="dominik@example.com",
            )

    def test_html_email_is_parsed(self):
        message = EmailMessage()

        message["Subject"] = "Job: Data Analyst"
        message["From"] = "jobs@example.com"
        message["To"] = "dominik@example.com"
        message["Message-ID"] = (
            "<job-html@example.com>"
        )
        message["Date"] = (
            "Wed, 28 Oct 2026 08:00:00 +0100"
        )

        message.set_content(
            """
            <html>
                <body>
                    <p>Unternehmen: Data GmbH</p>
                    <p>Standort: Paderborn</p>
                    <p>
                        https://jobs.example.com/data
                    </p>
                </body>
            </html>
            """,
            subtype="html",
        )

        parsed = parse_email_bytes(
            message.as_bytes(),
            mailbox="dominik@example.com",
        )

        self.assertEqual(
            parsed.title,
            "Data Analyst",
        )

        self.assertEqual(
            parsed.company,
            "Data GmbH",
        )

        self.assertEqual(
            parsed.location,
            "Paderborn",
        )

        self.assertEqual(
            parsed.job_url,
            "https://jobs.example.com/data",
        )

        self.assertEqual(
            parsed.category,
            JobCategory.DATA_ANALYST,
        )

    def test_missing_subject_is_rejected(self):
        message = EmailMessage()

        message["From"] = "jobs@example.com"
        message["To"] = "dominik@example.com"
        message["Message-ID"] = (
            "<missing-subject@example.com>"
        )
        message["Date"] = (
            "Wed, 28 Oct 2026 08:00:00 +0100"
        )

        message.set_content(
            "Unternehmen: Beispiel GmbH"
        )

        with self.assertRaisesMessage(
            ValueError,
            "Die E-Mail enthält keinen Betreff.",
        ):
            parse_email_bytes(
                message.as_bytes(),
                mailbox="dominik@example.com",
            )

    def test_missing_date_is_rejected(self):
        message = EmailMessage()

        message["Subject"] = (
            "Stellenangebot: Python Developer"
        )
        message["From"] = "jobs@example.com"
        message["To"] = "dominik@example.com"
        message["Message-ID"] = (
            "<missing-date@example.com>"
        )

        message.set_content(
            "Unternehmen: Beispiel GmbH"
        )

        with self.assertRaisesMessage(
            ValueError,
            "Die E-Mail enthält keinen Date-Header.",
        ):
            parse_email_bytes(
                message.as_bytes(),
                mailbox="dominik@example.com",
            )