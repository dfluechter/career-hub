from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import JobCategory, JobOffer, JobStatus


@login_required
def job_list(request):
    jobs = JobOffer.objects.all()

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    mailbox = request.GET.get("mailbox", "").strip()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(location__icontains=query)
        )

    valid_categories = {value for value, _ in JobCategory.choices}

    if category in valid_categories:
        jobs = jobs.filter(category=category)

    valid_statuses = {value for value, _ in JobStatus.choices}

    if status in valid_statuses:
        jobs = jobs.filter(status=status)

    if mailbox:
        jobs = jobs.filter(source_mailbox=mailbox)

    mailboxes = (
        JobOffer.objects
        .exclude(source_mailbox="")
        .values_list("source_mailbox", flat=True)
        .distinct()
        .order_by("source_mailbox")
    )

    paginator = Paginator(jobs, 20)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "job_count": paginator.count,
        "categories": JobCategory.choices,
        "statuses": JobStatus.choices,
        "mailboxes": mailboxes,
        "filters": {
            "q": query,
            "category": category,
            "status": status,
            "mailbox": mailbox,
        },
    }

    return render(
        request,
        "jobs/job_list.html",
        context,
    )