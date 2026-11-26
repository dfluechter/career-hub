from io import BytesIO
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Document, DocumentType


def create_docx_file(
    name: str = "test.docx",
) -> SimpleUploadedFile:
    """
    Erstellt eine minimale DOCX-Datei für Tests.

    DOCX-Dateien sind ZIP-Archive. Für unsere Upload-Validierung
    benötigen wir mindestens:
    - [Content_Types].xml
    - word/document.xml
    """

    buffer = BytesIO()

    with ZipFile(
        buffer,
        "w",
        ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<Types xmlns="'
                "http://schemas.openxmlformats.org/"
                'package/2006/content-types">'
                "</Types>"
            ),
        )

        archive.writestr(
            "word/document.xml",
            (
                '<w:document xmlns:w="'
                "http://schemas.openxmlformats.org/"
                'wordprocessingml/2006/main">'
                "</w:document>"
            ),
        )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    )


class DocumentViewTests(TestCase):
    def setUp(self):
        """
        Jeder Test erhält ein eigenes temporäres MEDIA_ROOT.
        Dadurch landen Test-DOCX-Dateien nicht im echten media/-Ordner.
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
        Einstellungen zurücksetzen und temporären Media-Ordner
        nach jedem Test entfernen.
        """

        self.override.disable()
        self.temp_media.cleanup()

    def test_document_list_requires_login(self):
        """
        Die Dokumentübersicht darf anonym nicht erreichbar sein.
        """

        self.client.logout()

        response = self.client.get(
            reverse(
                "documents:list",
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

    def test_document_can_be_uploaded(self):
        """
        Eine gültige DOCX-Datei kann als Dokument gespeichert werden.
        """

        response = self.client.post(
            reverse(
                "documents:create",
            ),
            {
                "title": (
                    "Lebenslauf Software Entwickler"
                ),
                "document_type": DocumentType.CV,
                "file": create_docx_file(),
                "description": "Testdokument",
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            Document.objects.count(),
            1,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.title,
            "Lebenslauf Software Entwickler",
        )

        self.assertEqual(
            document.document_type,
            DocumentType.CV,
        )

        self.assertTrue(
            document.active,
        )

        self.assertTrue(
            document.file.name.endswith(
                ".docx",
            )
        )

    def test_invalid_file_is_rejected(self):
        """
        Eine Nicht-DOCX-Datei darf nicht gespeichert werden.
        """

        invalid_file = SimpleUploadedFile(
            name="invalid.txt",
            content=b"not a docx file",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse(
                "documents:create",
            ),
            {
                "title": "Ungültiges Dokument",
                "document_type": DocumentType.CV,
                "file": invalid_file,
                "description": "",
                "active": True,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

        self.assertTrue(
            response.context["form"].errors,
        )

    def test_document_can_be_deactivated(self):
        """
        Ein aktives Dokument kann deaktiviert werden.
        """

        document = Document.objects.create(
            title="Test Lebenslauf",
            document_type=DocumentType.CV,
            file=create_docx_file(),
            active=True,
        )

        response = self.client.post(
            reverse(
                "documents:toggle-active",
                args=[
                    document.pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        document.refresh_from_db()

        self.assertFalse(
            document.active,
        )

    def test_document_can_be_downloaded(self):
        """
        Ein angemeldeter Benutzer kann ein Dokument herunterladen.

        FileResponse streamt die Datei. Unter Windows muss das
        Datei-Handle nach dem Test explizit geschlossen werden,
        damit TemporaryDirectory anschließend entfernt werden kann.

        response.close() wird hier bewusst NICHT verwendet.
        """

        document = Document.objects.create(
            title="Test Lebenslauf",
            document_type=DocumentType.CV,
            file=create_docx_file(),
            active=True,
        )

        response = self.client.get(
            reverse(
                "documents:download",
                args=[
                    document.pk,
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

            self.assertGreater(
                len(downloaded_content),
                0,
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

    def test_document_can_be_deleted(self):
        """
        Beim Löschen werden Datensatz und gespeicherte Datei entfernt.
        """

        document = Document.objects.create(
            title="Test Lebenslauf",
            document_type=DocumentType.CV,
            file=create_docx_file(),
            active=True,
        )

        document_pk = document.pk
        file_name = document.file.name
        storage = document.file.storage

        self.assertTrue(
            storage.exists(
                file_name,
            )
        )

        response = self.client.post(
            reverse(
                "documents:delete",
                args=[
                    document_pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            Document.objects.filter(
                pk=document_pk,
            ).exists()
        )

        self.assertFalse(
            storage.exists(
                file_name,
            )
        )