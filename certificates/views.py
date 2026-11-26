from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CertificateForm
from .models import Certificate, CertificateCategory


@login_required
def certificate_list(request):
    """
    Zeigt alle Zertifikate an.

    Unterstützte Filter:
    - Freitextsuche
    - Kategorie
    - Aktiv / Inaktiv
    """

    query = request.GET.get(
        "q",
        "",
    ).strip()

    category = request.GET.get(
        "category",
        "",
    ).strip()

    state = request.GET.get(
        "state",
        "",
    ).strip()

    certificates = Certificate.objects.all()

    # Freitextsuche
    if query:
        certificates = certificates.filter(
            Q(title__icontains=query)
            | Q(issuer__icontains=query)
            | Q(credential_id__icontains=query)
        )

    # Kategorie validieren
    valid_categories = {
        value
        for value, _ in CertificateCategory.choices
    }

    if category in valid_categories:
        certificates = certificates.filter(
            category=category,
        )

    # Aktiv / Inaktiv
    if state == "active":
        certificates = certificates.filter(
            active=True,
        )

    elif state == "inactive":
        certificates = certificates.filter(
            active=False,
        )

    context = {
        "certificates": certificates,
        "certificate_count": certificates.count(),
        "categories": CertificateCategory.choices,
        "query": query,
        "selected_category": category,
        "selected_state": state,
        "active_certificate_count": (
            Certificate.objects
            .filter(active=True)
            .count()
        ),
        "inactive_certificate_count": (
            Certificate.objects
            .filter(active=False)
            .count()
        ),
    }

    return render(
        request,
        "certificates/certificate_list.html",
        context,
    )


@login_required
def certificate_create(request):
    """
    Erstellt ein neues Zertifikat inklusive PDF-Datei.
    """

    if request.method == "POST":
        form = CertificateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            certificate = form.save()

            messages.success(
                request,
                f'„{certificate.title}“ wurde hochgeladen.',
            )

            return redirect(
                "certificates:list",
            )

    else:
        form = CertificateForm()

    context = {
        "form": form,
        "page_title": "Zertifikat hochladen",
        "submit_label": "Zertifikat speichern",
    }

    return render(
        request,
        "certificates/certificate_form.html",
        context,
    )


@login_required
def certificate_update(request, pk):
    """
    Bearbeitet ein vorhandenes Zertifikat.

    Wird dabei eine neue PDF hochgeladen,
    wird die bisherige Datei anschließend entfernt.
    """

    certificate = get_object_or_404(
        Certificate,
        pk=pk,
    )

    if request.method == "POST":
        old_file_name = certificate.file.name

        form = CertificateForm(
            request.POST,
            request.FILES,
            instance=certificate,
        )

        if form.is_valid():
            updated_certificate = form.save()

            new_file_name = updated_certificate.file.name

            if (
                old_file_name
                and old_file_name != new_file_name
            ):
                storage = updated_certificate.file.storage

                if storage.exists(old_file_name):
                    storage.delete(old_file_name)

            messages.success(
                request,
                (
                    f'„{updated_certificate.title}“ '
                    "wurde aktualisiert."
                ),
            )

            return redirect(
                "certificates:list",
            )

    else:
        form = CertificateForm(
            instance=certificate,
        )

    context = {
        "form": form,
        "certificate": certificate,
        "page_title": "Zertifikat bearbeiten",
        "submit_label": "Änderungen speichern",
    }

    return render(
        request,
        "certificates/certificate_form.html",
        context,
    )


@login_required
def certificate_download(request, pk):
    """
    Liefert die Zertifikats-PDF nur für
    authentifizierte Benutzer aus.
    """

    certificate = get_object_or_404(
        Certificate,
        pk=pk,
    )

    file_handle = certificate.file.open("rb")

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(
            certificate.file.name
        ).name,
    )


@login_required
@require_POST
def certificate_toggle_active(request, pk):
    """
    Schaltet ein Zertifikat zwischen
    Aktiv und Inaktiv um.
    """

    certificate = get_object_or_404(
        Certificate,
        pk=pk,
    )

    certificate.active = not certificate.active

    certificate.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    if certificate.active:
        message = (
            f'„{certificate.title}“ wurde aktiviert.'
        )
    else:
        message = (
            f'„{certificate.title}“ wurde deaktiviert.'
        )

    messages.success(
        request,
        message,
    )

    return redirect(
        "certificates:list",
    )


@login_required
@require_POST
def certificate_delete(request, pk):
    """
    Löscht sowohl den Datenbankeintrag
    als auch die dazugehörige PDF-Datei.
    """

    certificate = get_object_or_404(
        Certificate,
        pk=pk,
    )

    title = certificate.title
    file_name = certificate.file.name
    storage = certificate.file.storage

    certificate.delete()

    if (
        file_name
        and storage.exists(file_name)
    ):
        storage.delete(
            file_name,
        )

    messages.success(
        request,
        f'„{title}“ wurde gelöscht.',
    )

    return redirect(
        "certificates:list",
    )