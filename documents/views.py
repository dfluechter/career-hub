from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import DocumentForm
from .models import Document, DocumentType


@login_required
def document_list(request):
    selected_type = request.GET.get(
        "type",
        "",
    ).strip()

    selected_state = request.GET.get(
        "state",
        "",
    ).strip()

    query = request.GET.get(
        "q",
        "",
    ).strip()

    documents = Document.objects.all()

    valid_types = {
        value
        for value, _ in DocumentType.choices
    }

    if selected_type in valid_types:
        documents = documents.filter(
            document_type=selected_type,
        )

    if selected_state == "active":
        documents = documents.filter(
            active=True,
        )

    elif selected_state == "inactive":
        documents = documents.filter(
            active=False,
        )

    if query:
        documents = documents.filter(
            title__icontains=query,
        )

    context = {
        "documents": documents,
        "document_count": documents.count(),
        "document_types": DocumentType.choices,
        "selected_type": selected_type,
        "selected_state": selected_state,
        "query": query,
        "cv_count": Document.objects.filter(
            document_type=DocumentType.CV,
            active=True,
        ).count(),
        "cover_letter_count": Document.objects.filter(
            document_type=DocumentType.COVER_LETTER,
            active=True,
        ).count(),
    }

    return render(
        request,
        "documents/document_list.html",
        context,
    )


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            document = form.save()

            messages.success(
                request,
                f'„{document.title}“ wurde hochgeladen.',
            )

            return redirect(
                "documents:list",
            )

    else:
        form = DocumentForm()

    context = {
        "form": form,
        "page_title": "Dokument hochladen",
        "submit_label": "Dokument speichern",
    }

    return render(
        request,
        "documents/document_form.html",
        context,
    )


@login_required
def document_update(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
    )

    if request.method == "POST":
        old_file_name = document.file.name

        form = DocumentForm(
            request.POST,
            request.FILES,
            instance=document,
        )

        if form.is_valid():
            updated_document = form.save()

            new_file_name = updated_document.file.name

            if (
                old_file_name
                and old_file_name != new_file_name
            ):
                storage = updated_document.file.storage

                if storage.exists(old_file_name):
                    storage.delete(old_file_name)

            messages.success(
                request,
                f'„{updated_document.title}“ wurde aktualisiert.',
            )

            return redirect(
                "documents:list",
            )

    else:
        form = DocumentForm(
            instance=document,
        )

    context = {
        "form": form,
        "document": document,
        "page_title": "Dokument bearbeiten",
        "submit_label": "Änderungen speichern",
    }

    return render(
        request,
        "documents/document_form.html",
        context,
    )


@login_required
def document_download(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
    )

    file_handle = document.file.open("rb")

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(document.file.name).name,
    )


@login_required
@require_POST
def document_toggle_active(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
    )

    document.active = not document.active

    document.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    if document.active:
        message = (
            f'„{document.title}“ wurde aktiviert.'
        )
    else:
        message = (
            f'„{document.title}“ wurde deaktiviert.'
        )

    messages.success(
        request,
        message,
    )

    return redirect(
        "documents:list",
    )


@login_required
@require_POST
def document_delete(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
    )

    title = document.title
    file_name = document.file.name
    storage = document.file.storage

    document.delete()

    if file_name and storage.exists(file_name):
        storage.delete(file_name)

    messages.success(
        request,
        f'„{title}“ wurde gelöscht.',
    )

    return redirect(
        "documents:list",
    )