from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError

from .models import Certificate


MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate

        fields = (
            "title",
            "issuer",
            "category",
            "file",
            "issued_at",
            "expires_at",
            "credential_id",
            "credential_url",
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
                        "z. B. Python Professional Certificate"
                    ),
                }
            ),

            "issuer": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "placeholder": (
                        "z. B. Microsoft, Coursera oder Udemy"
                    ),
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                }
            ),

            "file": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full rounded-lg border "
                        "border-slate-700 bg-slate-950 "
                        "px-3 py-2.5 text-sm text-slate-300 "
                        "file:mr-4 file:rounded-md file:border-0 "
                        "file:bg-blue-600 file:px-3 file:py-2 "
                        "file:text-sm file:font-semibold "
                        "file:text-white hover:file:bg-blue-500"
                    ),
                    "accept": ".pdf,application/pdf",
                }
            ),

            "issued_at": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                }
            ),

            "expires_at": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                }
            ),

            "credential_id": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "placeholder": "Optionale Credential-ID",
                }
            ),

            "credential_url": forms.URLInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "placeholder": "https://...",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-slate-700 "
                        "bg-slate-950 px-3 py-2.5 text-slate-100 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "rows": 4,
                    "placeholder": (
                        "Optionale Beschreibung, erworbene "
                        "Kenntnisse oder Hinweise"
                    ),
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": (
                        "h-4 w-4 rounded border-slate-600 "
                        "bg-slate-950 text-blue-600 "
                        "focus:ring-blue-500"
                    ),
                }
            ),
        }

    def clean_file(self):
        """
        Validiert die Zertifikatsdatei.

        Anforderungen:
        - PDF-Dateiendung
        - maximal 15 MB
        - PDF-Dateisignatur beginnt mit %PDF-
        """

        uploaded_file = self.cleaned_data.get("file")

        # Beim Bearbeiten darf die bereits gespeicherte
        # Datei weiterverwendet werden.
        if not uploaded_file:
            if (
                self.instance.pk
                and self.instance.file
            ):
                return self.instance.file

            raise ValidationError(
                "Bitte wähle eine PDF-Datei aus."
            )

        suffix = Path(
            uploaded_file.name
        ).suffix.lower()

        if suffix != ".pdf":
            raise ValidationError(
                "Es sind ausschließlich PDF-Dateien erlaubt."
            )

        if uploaded_file.size > MAX_FILE_SIZE:
            raise ValidationError(
                "Die PDF-Datei darf maximal 15 MB groß sein."
            )

        header = uploaded_file.read(5)

        uploaded_file.seek(0)

        if header != b"%PDF-":
            raise ValidationError(
                "Die hochgeladene Datei ist keine gültige PDF-Datei."
            )

        return uploaded_file

    def clean(self):
        """
        Prüft feldübergreifende Abhängigkeiten.
        """

        cleaned_data = super().clean()

        issued_at = cleaned_data.get(
            "issued_at"
        )

        expires_at = cleaned_data.get(
            "expires_at"
        )

        if (
            issued_at
            and expires_at
            and expires_at < issued_at
        ):
            self.add_error(
                "expires_at",
                (
                    "Das Ablaufdatum darf nicht vor dem "
                    "Ausstellungsdatum liegen."
                ),
            )

        return cleaned_data