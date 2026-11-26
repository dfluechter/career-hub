from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jobs.models import (
    JobCategory,
    JobOffer,
    JobStatus,
)

from .models import (
    Application,
    ApplicationStatus,
)


class ApplicationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job = JobOffer.objects.create(
            title="Python Developer",
            company="Test Company",
            location="Lippstadt",
            category=JobCategory.SOFTWARE_DEVELOPER,
            source="test",
            source_mailbox="test@example.com",
            source_message_id="application-model-test",
            received_at=timezone.now(),
        )

    def test_application_can_be_created(self):
        application = Application.objects.create(
            job=self.job,
        )

        self.assertEqual(
            application.status,
            ApplicationStatus.PREPARING,
        )

        self.assertEqual(
            application.job,
            self.job,
        )


class ApplicationCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
        )

        cls.job = JobOffer.objects.create(
            title="Software Tester",
            company="Test Company",
            location="Lippstadt",
            category=JobCategory.SOFTWARE_TESTER,
            source="test",
            source_mailbox="test@example.com",
            source_message_id="application-view-test",
            received_at=timezone.now(),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_create_application(self):
        response = self.client.post(
            reverse(
                "applications:create",
                args=[self.job.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Application.objects.filter(
                job=self.job,
            ).exists()
        )

        self.job.refresh_from_db()

        self.assertEqual(
            self.job.status,
            JobStatus.PREPARING,
        )

    def test_application_is_not_duplicated(self):
        Application.objects.create(
            job=self.job,
        )

        self.client.post(
            reverse(
                "applications:create",
                args=[self.job.pk],
            )
        )

        self.assertEqual(
            Application.objects.filter(
                job=self.job,
            ).count(),
            1,
        )

    def test_create_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse(
                "applications:create",
                args=[self.job.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )