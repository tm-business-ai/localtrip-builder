from django.urls import path

from . import views


app_name = "plans"

urlpatterns = [
    path("new/", views.plan_request_create, name="create"),
    path("create/", views.plan_request_create, name="create_compat"),
    path("<int:pk>/preview/", views.plan_request_preview, name="preview"),
    path("<int:pk>/generate/", views.generate_plan_result, name="generate"),
    path("results/<int:pk>/", views.plan_result, name="result"),
    path("results/<int:pk>/pdf/", views.plan_result_pdf, name="result_pdf"),
    path("<int:pk>/result/", views.plan_request_latest_result, name="result_compat"),
]
