from django.test import SimpleTestCase

from jobs.models import JobCategory
from mail_import.services.classifier import (
    classify_job,
    normalize_text,
)


class JobClassifierTests(SimpleTestCase):
    def test_normalize_text(self):
        self.assertEqual(
            normalize_text(
                "  Python-Developer (Django)  "
            ),
            "python developer django",
        )

    def test_software_developer(self):
        result = classify_job(
            "Python Developer",
            "Django und PostgreSQL",
        )

        self.assertEqual(
            result,
            JobCategory.SOFTWARE_DEVELOPER,
        )

    def test_data_analyst(self):
        result = classify_job(
            "Data Analyst",
            "Power BI und Datenanalyse",
        )

        self.assertEqual(
            result,
            JobCategory.DATA_ANALYST,
        )

    def test_software_tester(self):
        result = classify_job(
            "QA Engineer",
            "Testautomatisierung",
        )

        self.assertEqual(
            result,
            JobCategory.SOFTWARE_TESTER,
        )

    def test_it_technician(self):
        result = classify_job(
            "IT Support Mitarbeiter",
            "Helpdesk und Service Desk",
        )

        self.assertEqual(
            result,
            JobCategory.IT_TECHNICIAN,
        )

    def test_unknown_category(self):
        result = classify_job(
            "Kaufmännischer Mitarbeiter",
            "Allgemeine Verwaltung",
        )

        self.assertEqual(
            result,
            JobCategory.OTHER,
        )