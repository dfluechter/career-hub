from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from mail_import.services.importer import import_email_bytes


class Command(BaseCommand):
    help = (
        "Importiert Stellenangebote aus lokalen "
        ".eml-Dateien oder Verzeichnissen."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="+",
            help=(
                "Eine oder mehrere .eml-Dateien "
                "oder Verzeichnisse."
            ),
        )

        parser.add_argument(
            "--mailbox",
            required=True,
            help=(
                "Quell-Postfach, zum Beispiel "
                "jobs@example.com."
            ),
        )

        parser.add_argument(
            "--source",
            default="eml",
            help=(
                "Bezeichnung der Importquelle. "
                "Standard: eml"
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ):
        mailbox = options["mailbox"]
        source = options["source"]

        files = self._collect_files(
            options["paths"]
        )

        if not files:
            raise CommandError(
                "Keine .eml-Dateien gefunden."
            )

        created_count = 0
        duplicate_count = 0
        error_count = 0

        self.stdout.write(
            f"{len(files)} E-Mail-Datei(en) gefunden."
        )

        for file_path in files:
            try:
                raw_message = file_path.read_bytes()

                result = import_email_bytes(
                    raw_message,
                    mailbox=mailbox,
                    source=source,
                )

            except (OSError, ValueError) as error:
                error_count += 1

                self.stderr.write(
                    self.style.ERROR(
                        f"[FEHLER] {file_path}: {error}"
                    )
                )

                continue

            if result.created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[NEU] {result.job.title}"
                    )
                )

            else:
                duplicate_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"[DUPLIKAT] {result.job.title}"
                    )
                )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Neu importiert: {created_count}"
            )
        )

        self.stdout.write(
            f"Duplikate: {duplicate_count}"
        )

        self.stdout.write(
            f"Fehler: {error_count}"
        )

    @staticmethod
    def _collect_files(
        raw_paths: list[str],
    ) -> list[Path]:
        files: list[Path] = []

        for raw_path in raw_paths:
            path = Path(raw_path).expanduser()

            if not path.exists():
                raise CommandError(
                    f"Pfad existiert nicht: {path}"
                )

            if path.is_file():
                if path.suffix.casefold() != ".eml":
                    raise CommandError(
                        "Nur .eml-Dateien können "
                        f"importiert werden: {path}"
                    )

                files.append(path)
                continue

            if path.is_dir():
                files.extend(
                    candidate
                    for candidate in path.rglob("*")
                    if (
                        candidate.is_file()
                        and candidate.suffix.casefold()
                        == ".eml"
    )
                )

                continue

            raise CommandError(
                f"Ungültiger Pfad: {path}"
            )

        return sorted(
            set(files),
            key=lambda item: str(item).casefold(),
        )