from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from applications.models import Application
from documents.models import Document, DocumentType
from jobs.models import JobOffer


@login_required
def dashboard(request):
    context = {
        "job_count": JobOffer.objects.count(),
        "application_count": Application.objects.count(),
        "document_count": Document.objects.count(),
        "certificate_count": 0,
        "cv_count": Document.objects.filter(
            document_type=DocumentType.CV,
            active=True,
        ).count(),
        "cover_letter_count": Document.objects.filter(
            document_type=DocumentType.COVER_LETTER,
            active=True,
        ).count(),
        "latest_jobs": JobOffer.objects.all()[:5],
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )