from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import JobCategory, JobOffer, JobStatus

class JobListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
        )

        cls.developer_job = JobOffer.objects.create(
            title="Python Developer",
            company="Test Company",
            location="Lippstadt",
            category=JobCategory.SOFTWARE_DEVELOPER,
            source="test",
            source_mailbox="test@example.com",
            source_message_id="test-dev-001",
            received_at=timezone.now(),
        )

        cls.data_job = JobOffer.objects.create(
            title="Data Analyst",
            company="Data Company",
            location="Paderborn",
            category=JobCategory.DATA_ANALYST,
            source="test",
            source_mailbox="second@example.com",
            source_message_id="test-data-001",
            received_at=timezone.now(),

        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_job_list_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("jobs:list")
        )

        self.assertEqual(response.status_code, 302)

    def test_job_detail_displays_job(self):
        response = self.client.get(
            reverse(
                "jobs:detail",
                args=[self.developer_job.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["job"],
            self.developer_job,
        )

        self.assertContains(
            response,
            "Python Developer",
        )

    def test_job_detail_returns_404(self):
        response = self.client.get(
            reverse(
                "jobs:detail",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_category_filter(self):
        response = self.client.get(
            reverse("jobs:list"),
            {
                "category":
                    JobCategory.DATA_ANALYST
            },
        )

        self.assertContains(
            response,
            "Data Analyst",
        )

        self.assertNotContains(
            response,
            "Python Developer",
        )

    def test_search_filter(self):
        response = self.client.get(
            reverse("jobs:list"),
            {"q": "Lippstadt"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        jobs = list(
            response.context["page_obj"].object_list
        )

        self.assertIn(
            self.developer_job,
            jobs,
        )

        self.assertNotIn(
            self.data_job,
            jobs,
        )

    def test_status_filter(self):
        self.developer_job.status = JobStatus.SAVED
        self.developer_job.save(update_fields=["status"])

        response = self.client.get(
            reverse("jobs:list"),
            {"status": JobStatus.SAVED},
        )

        self.assertEqual(response.status_code, 200)

        jobs = list(
            response.context["page_obj"].object_list
        )

        self.assertIn(self.developer_job, jobs)
        self.assertNotIn(self.data_job, jobs)

    def test_mailbox_filter(self):
        response = self.client.get(
            reverse("jobs:list"),
            {"mailbox": "test@example.com"},
        )

        self.assertEqual(response.status_code, 200)

        jobs = list(
            response.context["page_obj"].object_list
        )

        self.assertIn(self.developer_job, jobs)
        self.assertNotIn(self.data_job, jobs)

    def test_combined_filters(self):
        response = self.client.get(
            reverse("jobs:list"),
            {
                "q": "Lippstadt",
                "category": JobCategory.SOFTWARE_DEVELOPER,
                "status": JobStatus.NEW,
                "mailbox": "test@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)

        jobs = list(
            response.context["page_obj"].object_list
        )

        self.assertEqual(
            jobs,
            [self.developer_job],
        )

    def test_invalid_category_is_ignored(self):
        response = self.client.get(
            reverse("jobs:list"),
            {"category": "invalid-category"},
        )

        self.assertEqual(response.status_code, 200)

        jobs = list(
            response.context["page_obj"].object_list
        )

        self.assertIn(self.developer_job, jobs)
        self.assertIn(self.data_job, jobs)

    def test_job_detail_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                "jobs:detail",
                args=[self.developer_job.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_status_can_be_updated(self):
        response = self.client.post(
            reverse(
                "jobs:status-update",
                args=[self.developer_job.pk],
            ),
            {
                "status": JobStatus.SAVED,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.developer_job.refresh_from_db()

        self.assertEqual(
            self.developer_job.status,
            JobStatus.SAVED,
        )

    def test_invalid_status_is_rejected(self):
        original_status = self.developer_job.status

        response = self.client.post(
            reverse(
                "jobs:status-update",
                args=[self.developer_job.pk],
            ),
            {
                "status": "invalid-status",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.developer_job.refresh_from_db()

        self.assertEqual(
            self.developer_job.status,
            original_status,
        )

    def test_status_update_rejects_get(self):
        response = self.client.get(
            reverse(
                "jobs:status-update",
                args=[self.developer_job.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )