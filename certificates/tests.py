from datetime import date
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Certificate, CertificateCategory


def create_pdf_file(
    name: str = "certificate.pdf",
) -> SimpleUploadedFile:
    """
    Erstellt eine minimale PDF-Datei für Tests.

    Für unsere Formularvalidierung genügt eine Datei,
    deren Inhalt mit der PDF-Signatur %PDF- beginnt.
    """

    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog >>\n"
        b"endobj\n"
        b"trailer\n"
        b"<< /Root 1 0 R >>\n"
        b"%%EOF\n"
    )

    return SimpleUploadedFile(
        name=name,
        content=pdf_content,
        content_type="application/pdf",
    )


class CertificateViewTests(TestCase):
    def setUp(self):
        """
        Jeder Test verwendet einen eigenen temporären
        MEDIA_ROOT.

        Dadurch werden keine Test-PDFs im echten
        media/-Verzeichnis abgelegt.
        """

        self.temp_media = TemporaryDirectory()

        self.override = override_settings(
            MEDIA_ROOT=self.temp_media.name,
        )

        self.override.enable()

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
        )

        self.client.force_login(
            self.user,
        )

    def tearDown(self):
        """
        Temporäre Media-Konfiguration wieder entfernen.
        """

        self.override.disable()
        self.temp_media.cleanup()

    def create_certificate(
        self,
        *,
        title="Python Certificate",
        issuer="Test Academy",
        category=CertificateCategory.SOFTWARE_DEVELOPMENT,
        active=True,
    ):
        """
        Hilfsmethode für wiederkehrende Zertifikatserstellung.
        """

        return Certificate.objects.create(
            title=title,
            issuer=issuer,
            category=category,
            file=create_pdf_file(),
            issued_at=date(
                2026,
                1,
                15,
            ),
            credential_id="TEST-001",
            credential_url="https://example.com/credential",
            description="Testzertifikat",
            active=active,
        )

    def test_certificate_list_requires_login(self):
        """
        Die Zertifikatsübersicht ist geschützt.
        """

        self.client.logout()

        response = self.client.get(
            reverse(
                "certificates:list",
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_certificate_can_be_uploaded(self):
        """
        Eine gültige PDF-Datei kann als Zertifikat
        hochgeladen werden.
        """

        response = self.client.post(
            reverse(
                "certificates:create",
            ),
            {
                "title": "Python Professional Certificate",
                "issuer": "Test Academy",
                "category": (
                    CertificateCategory.SOFTWARE_DEVELOPMENT
                ),
                "file": create_pdf_file(),
                "issued_at": "2026-01-15",
                "expires_at": "",
                "credential_id": "PYTHON-001",
                "credential_url": (
                    "https://example.com/python-certificate"
                ),
                "description": "Python Testzertifikat",
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            Certificate.objects.count(),
            1,
        )

        certificate = Certificate.objects.get()

        self.assertEqual(
            certificate.title,
            "Python Professional Certificate",
        )

        self.assertEqual(
            certificate.issuer,
            "Test Academy",
        )

        self.assertEqual(
            certificate.category,
            CertificateCategory.SOFTWARE_DEVELOPMENT,
        )

        self.assertTrue(
            certificate.active,
        )

        self.assertTrue(
            certificate.file.name.endswith(
                ".pdf",
            )
        )

    def test_invalid_file_is_rejected(self):
        """
        Eine Datei ohne gültige PDF-Struktur
        darf nicht gespeichert werden.
        """

        invalid_file = SimpleUploadedFile(
            name="fake.pdf",
            content=b"This is not a PDF.",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse(
                "certificates:create",
            ),
            {
                "title": "Ungültiges Zertifikat",
                "issuer": "Test Academy",
                "category": CertificateCategory.OTHER,
                "file": invalid_file,
                "issued_at": "",
                "expires_at": "",
                "credential_id": "",
                "credential_url": "",
                "description": "",
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Certificate.objects.count(),
            0,
        )

        self.assertIn(
            "file",
            response.context["form"].errors,
        )

    def test_non_pdf_extension_is_rejected(self):
        """
        Auch eine Datei mit PDF-Inhalt, aber falscher
        Dateiendung, wird abgelehnt.
        """

        invalid_file = SimpleUploadedFile(
            name="certificate.txt",
            content=b"%PDF-1.4\n%%EOF\n",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse(
                "certificates:create",
            ),
            {
                "title": "Falsche Dateiendung",
                "issuer": "Test Academy",
                "category": CertificateCategory.OTHER,
                "file": invalid_file,
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Certificate.objects.count(),
            0,
        )

    def test_expiration_before_issue_date_is_rejected(self):
        """
        Das Ablaufdatum darf nicht vor dem
        Ausstellungsdatum liegen.
        """

        response = self.client.post(
            reverse(
                "certificates:create",
            ),
            {
                "title": "Test Certificate",
                "issuer": "Test Academy",
                "category": CertificateCategory.OTHER,
                "file": create_pdf_file(),
                "issued_at": "2026-06-01",
                "expires_at": "2026-05-01",
                "credential_id": "",
                "credential_url": "",
                "description": "",
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Certificate.objects.count(),
            0,
        )

        self.assertIn(
            "expires_at",
            response.context["form"].errors,
        )

    def test_certificate_can_be_deactivated(self):
        """
        Ein aktives Zertifikat kann deaktiviert werden.
        """

        certificate = self.create_certificate()

        response = self.client.post(
            reverse(
                "certificates:toggle-active",
                args=[
                    certificate.pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        certificate.refresh_from_db()

        self.assertFalse(
            certificate.active,
        )

    def test_certificate_can_be_reactivated(self):
        """
        Ein inaktives Zertifikat kann wieder aktiviert werden.
        """

        certificate = self.create_certificate(
            active=False,
        )

        response = self.client.post(
            reverse(
                "certificates:toggle-active",
                args=[
                    certificate.pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        certificate.refresh_from_db()

        self.assertTrue(
            certificate.active,
        )

    def test_certificate_can_be_downloaded(self):
        """
        Eine Zertifikats-PDF kann heruntergeladen werden.

        Der FileResponse-Dateistream wird unter Windows
        explizit geschlossen, damit TemporaryDirectory
        anschließend gelöscht werden kann.
        """

        certificate = self.create_certificate()

        response = self.client.get(
            reverse(
                "certificates:download",
                args=[
                    certificate.pk,
                ],
            )
        )

        try:
            self.assertEqual(
                response.status_code,
                200,
            )

            self.assertTrue(
                response.streaming,
            )

            self.assertIn(
                "attachment",
                response["Content-Disposition"],
            )

            downloaded_content = b"".join(
                response.streaming_content
            )

            self.assertTrue(
                downloaded_content.startswith(
                    b"%PDF-",
                )
            )

        finally:
            file_to_stream = getattr(
                response,
                "file_to_stream",
                None,
            )

            if (
                file_to_stream is not None
                and not file_to_stream.closed
            ):
                file_to_stream.close()

    def test_certificate_can_be_deleted(self):
        """
        Beim Löschen werden Datensatz und PDF-Datei entfernt.
        """

        certificate = self.create_certificate()

        certificate_pk = certificate.pk
        file_name = certificate.file.name
        storage = certificate.file.storage

        self.assertTrue(
            storage.exists(
                file_name,
            )
        )

        response = self.client.post(
            reverse(
                "certificates:delete",
                args=[
                    certificate_pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            Certificate.objects.filter(
                pk=certificate_pk,
            ).exists()
        )

        self.assertFalse(
            storage.exists(
                file_name,
            )
        )

    def test_category_filter(self):
        """
        Die Übersicht kann nach Kategorie filtern.
        """

        development_certificate = self.create_certificate(
            title="Python Certificate",
            category=(
                CertificateCategory.SOFTWARE_DEVELOPMENT
            ),
        )

        data_certificate = self.create_certificate(
            title="Data Analysis Certificate",
            category=CertificateCategory.DATA_ANALYSIS,
        )

        response = self.client.get(
            reverse(
                "certificates:list",
            ),
            {
                "category": CertificateCategory.DATA_ANALYSIS,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        certificates = list(
            response.context["certificates"]
        )

        self.assertIn(
            data_certificate,
            certificates,
        )

        self.assertNotIn(
            development_certificate,
            certificates,
        )

    def test_search_filter(self):
        """
        Die Freitextsuche berücksichtigt Titel,
        Anbieter und Credential-ID.
        """

        python_certificate = self.create_certificate(
            title="Python Professional",
            issuer="Python Academy",
        )

        data_certificate = self.create_certificate(
            title="Data Analyst",
            issuer="Data Academy",
        )

        response = self.client.get(
            reverse(
                "certificates:list",
            ),
            {
                "q": "Python",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        certificates = list(
            response.context["certificates"]
        )

        self.assertIn(
            python_certificate,
            certificates,
        )

        self.assertNotIn(
            data_certificate,
            certificates,
        )

    def test_active_filter(self):
        """
        Die Übersicht kann nur aktive Zertifikate anzeigen.
        """

        active_certificate = self.create_certificate(
            title="Active Certificate",
            active=True,
        )

        inactive_certificate = self.create_certificate(
            title="Inactive Certificate",
            active=False,
        )

        response = self.client.get(
            reverse(
                "certificates:list",
            ),
            {
                "state": "active",
            },
        )

        certificates = list(
            response.context["certificates"]
        )

        self.assertIn(
            active_certificate,
            certificates,
        )

        self.assertNotIn(
            inactive_certificate,
            certificates,
        )