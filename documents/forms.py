from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django import forms
from django.core.exceptions import ValidationError

from .models import Document


MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document

        fields = (
            "title",
            "document_type",
            "file",
            "description",
            "active",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "placeholder": (
                        "z. B. Lebenslauf Software Entwickler"
                    ),
                }
            ),
            "document_type": forms.Select(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100"
                    ),
                }
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full rounded-lg border "
                        "border-slate-700 bg-slate-950 "
                        "px-3 py-2.5 text-sm text-slate-300"
                    ),
                    "accept": ".docx",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100"
                    ),
                    "rows": 4,
                }
            ),
            "active": forms.CheckboxInput(
                attrs={
                    "class": (
                        "h-4 w-4 rounded border-slate-600 "
                        "bg-slate-950 text-blue-600"
                    ),
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            if self.instance.pk and self.instance.file:
                return self.instance.file

            raise ValidationError(
                "Bitte wähle eine DOCX-Datei aus."
            )

        suffix = Path(uploaded_file.name).suffix.lower()

        if suffix != ".docx":
            raise ValidationError(
                "Es sind ausschließlich DOCX-Dateien erlaubt."
            )

        if uploaded_file.size > MAX_FILE_SIZE:
            raise ValidationError(
                "Die Datei darf maximal 10 MB groß sein."
            )

        try:
            with ZipFile(uploaded_file) as archive:
                names = set(archive.namelist())

                if "[Content_Types].xml" not in names:
                    raise ValidationError(
                        "Die Datei ist kein gültiges Word-Dokument."
                    )

                if "word/document.xml" not in names:
                    raise ValidationError(
                        "Die Datei enthält kein gültiges "
                        "Word-Hauptdokument."
                    )

        except BadZipFile as error:
            raise ValidationError(
                "Die Datei ist kein gültiges DOCX-Dokument."
            ) from error

        finally:
            uploaded_file.seek(0)

        return uploaded_file