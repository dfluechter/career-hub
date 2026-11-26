from django.urls import path

from . import views


app_name = "jobs"

urlpatterns = [
    path(
        "",
        views.job_list,
        name="list",
    ),
    path(
        "<int:pk>/",
        views.job_detail,
        name="detail",
    ),
    path(
        "<int:pk>/status/",
        views.job_status_update,
        name="status-update",
    ),
]