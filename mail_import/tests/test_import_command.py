from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from jobs.models import JobOffer


def build_eml(
    *,
    message_id: str = "<command-test-001@example.com>",
    title: str = "Backend Developer",
    company: str = "Test GmbH",
    location: str = "Lippstadt",
) -> bytes:
    """
    Erstellt eine minimale RFC-kompatible E-Mail
    als Bytes für die Command-Tests.
    """

    content = (
        "From: jobs@example.com\r\n"
        "To: dominik@example.com\r\n"
        f"Subject: Stellenangebot: {title}\r\n"
        f"Message-ID: {message_id}\r\n"
        "Date: Wed, 28 Oct 2026 08:00:00 +0100\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Transfer-Encoding: 8bit\r\n"
        "\r\n"
        f"Stellenbezeichnung: {title}\r\n"
        f"Unternehmen: {company}\r\n"
        f"Standort: {location}\r\n"
        "https://jobs.example.com/job\r\n"
    )

    return content.encode("utf-8")


class ImportJobsCommandTests(TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()

        self.directory = Path(
            self.temp_directory.name
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def create_eml(
        self,
        filename: str,
        *,
        message_id: str,
        title: str = "Backend Developer",
        company: str = "Test GmbH",
        location: str = "Lippstadt",
    ) -> Path:
        """
        Schreibt eine Test-Mail ohne PowerShell-
        Encoding/BOM-Probleme direkt als Bytes.
        """

        path = self.directory / filename

        path.write_bytes(
            build_eml(
                message_id=message_id,
                title=title,
                company=company,
                location=location,
            )
        )

        return path

    def run_import(
        self,
        *paths: Path,
        mailbox: str = "dominik@example.com",
        source: str = "test-eml",
    ) -> tuple[str, str]:
        """
        Führt import_jobs aus und gibt stdout/stderr zurück.
        """

        stdout = StringIO()
        stderr = StringIO()

        call_command(
            "import_jobs",
            *[
                str(path)
                for path in paths
            ],
            mailbox=mailbox,
            source=source,
            stdout=stdout,
            stderr=stderr,
            no_color=True,
        )

        return (
            stdout.getvalue(),
            stderr.getvalue(),
        )

    def test_single_eml_is_imported(self):
        path = self.create_eml(
            "backend.eml",
            message_id=(
                "<single-command@example.com>"
            ),
        )

        stdout, stderr = self.run_import(
            path,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

        job = JobOffer.objects.get()

        self.assertEqual(
            job.title,
            "Backend Developer",
        )

        self.assertEqual(
            job.company,
            "Test GmbH",
        )

        self.assertEqual(
            job.location,
            "Lippstadt",
        )

        self.assertEqual(
            job.source,
            "test-eml",
        )

        self.assertEqual(
            job.source_mailbox,
            "dominik@example.com",
        )

        self.assertIn(
            "[NEU] Backend Developer",
            stdout,
        )

        self.assertIn(
            "Neu importiert: 1",
            stdout,
        )

        self.assertIn(
            "Duplikate: 0",
            stdout,
        )

        self.assertIn(
            "Fehler: 0",
            stdout,
        )

        self.assertEqual(
            stderr,
            "",
        )

    def test_same_eml_is_not_imported_twice(self):
        path = self.create_eml(
            "duplicate.eml",
            message_id=(
                "<duplicate-command@example.com>"
            ),
        )

        first_stdout, _ = self.run_import(
            path,
        )

        second_stdout, _ = self.run_import(
            path,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

        self.assertIn(
            "Neu importiert: 1",
            first_stdout,
        )

        self.assertIn(
            "[DUPLIKAT] Backend Developer",
            second_stdout,
        )

        self.assertIn(
            "Neu importiert: 0",
            second_stdout,
        )

        self.assertIn(
            "Duplikate: 1",
            second_stdout,
        )

    def test_directory_imports_all_eml_files(self):
        self.create_eml(
            "backend.eml",
            message_id=(
                "<directory-backend@example.com>"
            ),
            title="Backend Developer",
        )

        self.create_eml(
            "data.eml",
            message_id=(
                "<directory-data@example.com>"
            ),
            title="Data Analyst",
            company="Data GmbH",
            location="Paderborn",
        )

        stdout, stderr = self.run_import(
            self.directory,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            2,
        )

        self.assertTrue(
            JobOffer.objects.filter(
                title="Backend Developer",
            ).exists()
        )

        self.assertTrue(
            JobOffer.objects.filter(
                title="Data Analyst",
            ).exists()
        )

        self.assertIn(
            "2 E-Mail-Datei(en) gefunden.",
            stdout,
        )

        self.assertIn(
            "Neu importiert: 2",
            stdout,
        )

        self.assertIn(
            "Duplikate: 0",
            stdout,
        )

        self.assertIn(
            "Fehler: 0",
            stdout,
        )

        self.assertEqual(
            stderr,
            "",
        )

    def test_nested_directory_is_scanned(self):
        nested = (
            self.directory
            / "provider"
            / "jobs"
        )

        nested.mkdir(
            parents=True,
        )

        path = nested / "nested.eml"

        path.write_bytes(
            build_eml(
                message_id=(
                    "<nested-command@example.com>"
                ),
                title="Software Tester",
            )
        )

        stdout, _ = self.run_import(
            self.directory,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

        self.assertTrue(
            JobOffer.objects.filter(
                title="Software Tester",
            ).exists()
        )

        self.assertIn(
            "Neu importiert: 1",
            stdout,
        )

    def test_non_existing_path_is_rejected(self):
        missing = (
            self.directory
            / "does-not-exist.eml"
        )

        with self.assertRaisesMessage(
            CommandError,
            "Pfad existiert nicht:",
        ):
            self.run_import(
                missing,
            )

        self.assertEqual(
            JobOffer.objects.count(),
            0,
        )

    def test_non_eml_file_is_rejected(self):
        path = (
            self.directory
            / "job.txt"
        )

        path.write_text(
            "Not an EML file.",
            encoding="utf-8",
        )

        with self.assertRaisesMessage(
            CommandError,
            "Nur .eml-Dateien können importiert werden:",
        ):
            self.run_import(
                path,
            )

        self.assertEqual(
            JobOffer.objects.count(),
            0,
        )

    def test_invalid_email_is_reported_as_error(self):
        path = (
            self.directory
            / "invalid.eml"
        )

        path.write_bytes(
            (
                b"From: jobs@example.com\r\n"
                b"Subject: Invalid Job\r\n"
                b"\r\n"
                b"Missing Message-ID."
            )
        )

        stdout, stderr = self.run_import(
            path,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            0,
        )

        self.assertIn(
            "Neu importiert: 0",
            stdout,
        )

        self.assertIn(
            "Duplikate: 0",
            stdout,
        )

        self.assertIn(
            "Fehler: 1",
            stdout,
        )

        self.assertIn(
            "[FEHLER]",
            stderr,
        )

        self.assertIn(
            "keine Message-ID",
            stderr,
        )

    def test_non_eml_files_inside_directory_are_ignored(self):
        self.create_eml(
            "valid.eml",
            message_id=(
                "<ignore-other-files@example.com>"
            ),
        )

        text_file = (
            self.directory
            / "notes.txt"
        )

        text_file.write_text(
            "Ignore me.",
            encoding="utf-8",
        )

        stdout, _ = self.run_import(
            self.directory,
        )

        self.assertEqual(
            JobOffer.objects.count(),
            1,
        )

        self.assertIn(
            "1 E-Mail-Datei(en) gefunden.",
            stdout,
        )

    def test_empty_directory_is_rejected(self):
        with self.assertRaisesMessage(
            CommandError,
            "Keine .eml-Dateien gefunden.",
        ):
            self.run_import(
                self.directory,
            )

        self.assertEqual(
            JobOffer.objects.count(),
            0,
        )