from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "api/reports-app/mooe/download/<str:report_type>/",
        views.download_mooe,
        name="download_mooe",
    ),
    path(
        "api/reports-app/fund/download/<str:report_type>/",
        views.download_fund,
        name="download_fund",
    ),
    path("api/reports-app/", include("reports_app.api_urls")),
]
