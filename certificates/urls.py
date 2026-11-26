from django.urls import path

from . import views


app_name = "certificates"


urlpatterns = [
    # Übersicht
    path(
        "",
        views.certificate_list,
        name="list",
    ),

    # Neues Zertifikat hochladen
    path(
        "upload/",
        views.certificate_create,
        name="create",
    ),

    # Zertifikat bearbeiten
    path(
        "<int:pk>/edit/",
        views.certificate_update,
        name="update",
    ),

    # PDF herunterladen
    path(
        "<int:pk>/download/",
        views.certificate_download,
        name="download",
    ),

    # Aktiv / Inaktiv umschalten
    path(
        "<int:pk>/toggle-active/",
        views.certificate_toggle_active,
        name="toggle-active",
    ),

    # Zertifikat löschen
    path(
        "<int:pk>/delete/",
        views.certificate_delete,
        name="delete",
    ),
]