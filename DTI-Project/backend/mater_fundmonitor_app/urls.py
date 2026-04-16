from django.urls import include, path

from . import views

urlpatterns = [
    # Monitoring APIs
    path("api/mooe-budget/", views.get_mooe_budget, name="get_mooe_budget"),
    path("api/mater-fundmonitor-app/", include("mater_fundmonitor_app.api_urls")),
]
