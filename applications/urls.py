from django.urls import path

from . import views


app_name = "applications"


urlpatterns = [
    path(
        "",
        views.application_list,
        name="list",
    ),
    path(
        "create/<int:job_pk>/",
        views.application_create,
        name="create",
    ),
]