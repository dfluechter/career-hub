from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from jobs.models import JobOffer


@login_required
def dashboard(request):
    context = {
        "job_count": JobOffer.objects.count(),
        "latest_jobs": JobOffer.objects.all()[:5],
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )