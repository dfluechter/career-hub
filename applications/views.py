from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from jobs.models import JobOffer, JobStatus

from .models import Application


@login_required
def application_list(request):
    """Zeigt alle vorhandenen Bewerbungen an."""

    applications = (
        Application.objects
        .select_related(
            "job",
            "cv",
            "cover_letter",
        )
        .all()
    )

    context = {
        "applications": applications,
        "application_count": applications.count(),
    }

    return render(
        request,
        "applications/application_list.html",
        context,
    )


@login_required
@require_POST
def application_create(request, job_pk):
    """Erstellt für ein Stellenangebot eine Bewerbung."""

    job = get_object_or_404(
        JobOffer,
        pk=job_pk,
    )

    application, created = Application.objects.get_or_create(
        job=job,
    )

    if created:
        job.status = JobStatus.PREPARING

        job.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Bewerbung wurde angelegt.",
        )
    else:
        messages.info(
            request,
            "Für diese Stelle existiert bereits eine Bewerbung.",
        )

    return redirect(
        "jobs:detail",
        pk=job.pk,
    )