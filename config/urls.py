from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            pattern_name="dashboard:index",
            permanent=False,
        ),
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("jobs/", include("jobs.urls")),
    path(
        "applications/",
        include("applications.urls"),
    ),
    path(
        "documents/",
        include("documents.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )