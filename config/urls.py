from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("plans/", include("apps.plans.urls")),
    path("", include("apps.core.urls")),
]
