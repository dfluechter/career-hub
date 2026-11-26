# 💼 Career Hub

> Persönliches Bewerbungsmanagement mit Django, PostgreSQL, Tailwind CSS und einem modularen Mail-Import.

## 🚀 Überblick

Career Hub bündelt den Bewerbungsprozess in einer lokalen Webanwendung:

- 📊 Dashboard mit Kennzahlen
- 💼 Stellenangebote mit Suche, Filtern, Detailseite und Status
- 📝 Bewerbungen mit Lebenslauf- und Anschreiben-Zuordnung
- 📄 Dokumentverwaltung für DOCX-Dateien
- 🎓 Zertifikatsverwaltung für PDF-Dateien und Credential-Metadaten
- ✉️ Mail-Parser zur Erkennung und Klassifizierung von Stellenangeboten
- 🧪 automatisierte Django-Tests

## 🧰 Tech Stack

| Tool | Version / Vorgabe | Zweck |
|---|---|---|
| 🐍 Python | 3.12 | Laufzeit |
| 🌐 Django | `>=5.2,<5.3` | Webframework |
| 🐘 PostgreSQL | 17.x lokal | Datenbank |
| 🎨 django-tailwind-cli | `>=4.8.2` | Tailwind-Integration |
| 🗃️ psycopg | `>=3.3.6` | PostgreSQL-Treiber |
| 🔐 python-dotenv | `>=1.2.4` | Umgebungsvariablen |
| 📦 uv | aktuell lokal installiert | Python-Projekt- und Paketverwaltung |
| 🔀 Git / GitHub | `main` | Versionsverwaltung |

> Maßgeblich für Python-Abhängigkeiten sind `pyproject.toml` und `uv.lock`.

## 📁 Projektstruktur

```text
career-hub/
├── applications/        # Bewerbungen
├── certificates/        # Zertifikate
├── config/              # Django-Konfiguration
├── dashboard/           # Dashboard
├── documents/           # Lebensläufe / Anschreiben
├── jobs/                # Stellenangebote
├── mail_import/         # Mail-Parser und Importlogik
├── templates/           # gemeinsame Django-Templates
├── assets/              # statische Assets / Tailwind-CSS
├── media/               # lokale Uploads, nicht committen
├── manage.py
├── pyproject.toml
├── uv.lock
└── .env.example
```

## 🖥️ Voraussetzungen

Für die lokale Windows-Entwicklung werden benötigt:

1. Git
2. Python 3.12
3. uv
4. PostgreSQL 17
5. ein aktuelles PowerShell-Terminal

Versionen prüfen:

```powershell
python --version
uv --version
psql --version
git --version
```

## 📥 Repository lokal klonen

```powershell
cd D:\dev
git clone https://github.com/dfluechter/career-hub.git
cd career-hub
```

Remote prüfen:

```powershell
git remote -v
```

Aktuellen Branch prüfen:

```powershell
git branch --show-current
```

Erwartet:

```text
main
```

## 📦 Python-Umgebung installieren

Die Abhängigkeiten sind in `pyproject.toml` und `uv.lock` definiert.

```powershell
uv sync
```

Django prüfen:

```powershell
uv run python manage.py check
```

## 🔐 Umgebungsvariablen

Vorlage kopieren:

```powershell
Copy-Item .env.example .env
```

Beispiel:

```dotenv
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True

DATABASE_NAME=career_hub
DATABASE_USER=career_hub_user
DATABASE_PASSWORD=change-me
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

> ⚠️ Niemals echte Passwörter oder Secrets committen.

Prüfen, ob `.env` ignoriert wird:

```powershell
git check-ignore .env
```

## 🐘 PostgreSQL einrichten

Als PostgreSQL-Administrator anmelden:

```powershell
psql -U postgres -h localhost -d postgres
```

Beispiel für die lokale Datenbank und Rolle:

```sql
CREATE ROLE career_hub_user WITH LOGIN PASSWORD 'DEIN_LOKALES_PASSWORT';
CREATE DATABASE career_hub OWNER career_hub_user;
```

Für lokale Django-Testdatenbanken benötigt die Entwicklungsrolle `CREATEDB`:

```sql
ALTER ROLE career_hub_user CREATEDB;
```

Beenden:

```text
\q
```

Verbindung testen:

```powershell
psql -U career_hub_user -h localhost -d career_hub
```

Django-Verbindung prüfen:

```powershell
uv run python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.settings_dict['USER'], connection.settings_dict['NAME'], connection.vendor)"
```

## 🗄️ Migrationen

Status prüfen:

```powershell
uv run python manage.py showmigrations
```

Neue Migrationen erstellen:

```powershell
uv run python manage.py makemigrations
```

Migrationen anwenden:

```powershell
uv run python manage.py migrate
```

SQL einer Migration ansehen:

```powershell
uv run python manage.py sqlmigrate APP MIGRATION
```

Beispiel:

```powershell
uv run python manage.py sqlmigrate certificates 0001
```

## 👤 Admin-Benutzer

Falls noch kein Superuser existiert:

```powershell
uv run python manage.py createsuperuser
```

Admin-Oberfläche:

```text
http://127.0.0.1:8000/admin/
```

## ▶️ Entwicklungsserver

```powershell
uv run python manage.py runserver
```

Wichtige lokale URLs:

```text
http://127.0.0.1:8000/dashboard/
http://127.0.0.1:8000/jobs/
http://127.0.0.1:8000/applications/
http://127.0.0.1:8000/documents/
http://127.0.0.1:8000/certificates/
http://127.0.0.1:8000/admin/
```

> Der Django-Development-Server ist ausschließlich für lokale Entwicklung vorgesehen.

## 🎨 Tailwind CSS

CSS-Build:

```powershell
uv run python manage.py tailwind build
```

Danach Django separat starten:

```powershell
uv run python manage.py runserver
```

### Windows-Hinweis

Auf dem aktuellen Windows-Setup trat beim Standalone-Tailwind-Binary ein `ERR_DLOPEN_FAILED` in Verbindung mit `lightningcss.win32-x64-msvc.node` auf. Deshalb wird der Django-Server unabhängig vom Tailwind-Watcher gestartet.

```powershell
uv run python manage.py runserver
```

## 🧪 Tests

Alle aktuell relevanten Fachbereiche (aktueller geprüfter Stand: **47 Tests erfolgreich**):

```powershell
uv run python manage.py test jobs applications documents certificates mail_import
```

Einzelne Apps:

```powershell
uv run python manage.py test jobs
uv run python manage.py test applications
uv run python manage.py test documents
uv run python manage.py test certificates
uv run python manage.py test mail_import
```

Mail-Parser isoliert:

```powershell
uv run python manage.py test mail_import.tests.test_parser -v 2
```

Classifier isoliert:

```powershell
uv run python manage.py test mail_import.tests.test_classifier -v 2
```

Systemcheck:

```powershell
uv run python manage.py check
```

## 💼 Stellenangebote

Die `jobs`-App verwaltet unter anderem:

- Stellenbezeichnung
- Unternehmen
- Standort
- Kategorie
- Status
- Quelle
- Quell-Postfach
- Message-ID
- Stellen-URL
- Eingangsdatum

Zielprofile:

- 🛠️ IT-Techniker
- 💻 Software Entwickler
- 📊 Data Analyst
- 🧪 Software Tester

Die `source_message_id` dient als Datenbank-Schutz gegen doppelte Mail-Imports.

## 📝 Bewerbungen

Eine Bewerbung ist einem `JobOffer` zugeordnet und kann Bewerbungsunterlagen referenzieren.

Workflow:

```text
Neu
 → Gemerkt
 → Bewerbung vorbereiten
 → Beworben
 → Vorstellungsgespräch
 → Zusage / Absage
```

## 📄 Dokumente

Unterstützt werden aktuell DOCX-Dateien für:

- Lebensläufe
- Anschreiben

Funktionen:

- Upload
- Bearbeiten
- Suche / Filter
- Aktiv / Inaktiv
- geschützter Download
- Löschen

Lokale Dateien landen unter:

```text
media/documents/YYYY/MM/
```

`media/` darf nicht versioniert werden.

## 🎓 Zertifikate

Zertifikate werden separat von Bewerbungsdokumenten verwaltet.

Metadaten:

- Zertifikatsname
- Anbieter
- Kategorie
- PDF
- Ausstellungsdatum
- Ablaufdatum
- Credential-ID
- Credential-URL
- Beschreibung
- Aktiv / Inaktiv

Lokale PDFs:

```text
media/certificates/YYYY/MM/
```

## ✉️ Mail-Import

Der aktuelle Mail-Import ist modular aufgebaut:

```text
E-Mail
  ↓
parser.py
  ↓
ParsedJobEmail
  ↓
classifier.py
  ↓
Job-Kategorie
  ↓
importer.py
  ↓
Duplikatprüfung via Message-ID
  ↓
JobOffer
```

### Parser

Verarbeitet unter anderem:

- MIME-E-Mails
- `text/plain`
- HTML-Mail
- Message-ID
- Absender
- Betreff
- Datum
- Jobtitel
- Unternehmen
- Standort
- Stellen-URL

### Klassifizierung

Aktuell deterministisch über Keywords für:

```text
software_developer
data_analyst
software_tester
it_technician
other
```

### Importer

**Status: Phase 4.2 in Arbeit.** Der nächste Schritt überführt `ParsedJobEmail` duplikatsicher in `JobOffer`. Die `source_message_id` ist bereits als eindeutige Datenbankkennung im Job-Modell vorgesehen.

## 🔎 Django-Shell

Starten:

```powershell
uv run python manage.py shell
```

Jobs prüfen:

```python
from jobs.models import JobOffer
JobOffer.objects.all()
```

Dokumente prüfen:

```python
from documents.models import Document
Document.objects.all()
```

Zertifikate prüfen:

```python
from certificates.models import Certificate
Certificate.objects.all()
```

Bewerbungen prüfen:

```python
from applications.models import Application
Application.objects.all()
```

## 🔗 URL-Namen prüfen

Beispiel:

```powershell
uv run python manage.py shell -c "from django.urls import reverse; print(reverse('dashboard:index')); print(reverse('jobs:list')); print(reverse('applications:list')); print(reverse('documents:list')); print(reverse('certificates:list'))"
```

Erwartete Pfade:

```text
/dashboard/
/jobs/
/applications/
/documents/
/certificates/
```

## 🧹 Git-Workflow

Status:

```powershell
git status --short
```

Diff:

```powershell
git diff
```

Änderungen stagen:

```powershell
git add .
```

Commit:

```powershell
git commit -m "feat: describe change"
```

Push:

```powershell
git push origin main
```

Historie:

```powershell
git log --oneline -5
```

## 🔒 Vor jedem Push

```powershell
git check-ignore .env
git check-ignore media
uv run python manage.py check
uv run python manage.py test jobs applications documents certificates mail_import
git status --short
```

Prüfen:

- `.env` nicht committen
- `media/` nicht committen
- keine Passwörter / Tokens im Code
- Migrationen committen
- Tests grün
- Django-Systemcheck grün

## 🩺 Troubleshooting

### PostgreSQL Passwort vergessen

Als Administrator in PostgreSQL anmelden:

```powershell
psql -U postgres -h localhost -d postgres
```

Dann interaktiv:

```text
\password career_hub_user
```

Anschließend dasselbe Passwort in `.env` eintragen.

### `permission denied to create database`

Lokale Testrolle:

```sql
ALTER ROLE career_hub_user CREATEDB;
```

### `NoReverseMatch`

URL-Name prüfen:

```powershell
uv run python manage.py shell -c "from django.urls import reverse; print(reverse('app:list'))"
```

### `TemplateDoesNotExist`

Template-Pfad prüfen:

```powershell
Test-Path templates\applications\application_list.html
```

Django-Loader prüfen:

```powershell
uv run python manage.py shell -c "from django.template.loader import get_template; print(get_template('applications/application_list.html').origin.name)"
```

### Migrationen prüfen

```powershell
uv run python manage.py showmigrations
```

### Tailwind-Binary unter Windows

Wenn `ERR_DLOPEN_FAILED` / `lightningcss.win32-x64-msvc.node` auftritt, Django unabhängig starten:

```powershell
uv run python manage.py runserver
```

## 🗺️ Projektstatus

```text
Phase 1  Django / PostgreSQL / Auth      ✅
Phase 2  JobOffer / Filter / Details     ✅
Phase 3  Applications / Documents        ✅
          Zertifikate                    ✅
Phase 4.1 Mail-Parser / Classifier       ✅
Phase 4.2 Duplikatsicherer Importer      🚧
Phase 4.3 Management Command             ⏳
Phase 4.4 Mail-Provider-Anbindung        ⏳
```

## ✅ Aktuell verifizierter Entwicklungsstand

```text
Django-Systemcheck                         ✅
Jobs / Applications / Documents / Certs   ✅
Mail-Classifier                            ✅ 6 Tests
Mail-Parser                                ✅ 6 Tests
Gesamtsuite                                ✅ 47 Tests
Zertifikatsverwaltung                      ✅
Dokumentverwaltung                         ✅
Phase 4.2 Importer                         🚧 als Nächstes
```

Letzter im Gespräch bestätigter GitHub-Commit für die Zertifikatsverwaltung:

```text
585d07f feat: add certificate management
```

## 📌 Repository

```text
https://github.com/dfluechter/career-hub
```

## 👤 Autor

**Dominik Flüchter**

Career Hub ist ein persönliches Portfolio- und Automatisierungsprojekt für strukturiertes Bewerbungsmanagement.
