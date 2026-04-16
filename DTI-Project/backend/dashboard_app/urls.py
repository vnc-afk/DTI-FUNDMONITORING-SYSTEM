from django.urls import include, path

from dashboard_app.views import api

urlpatterns = [
    # API endpoints for dashboard data and lookups
    path("api/dashboard/kpis/", api.get_dashboard_kpis, name="api_dashboard_kpis"),
    path(
        "api/dashboard/charts/", api.get_dashboard_charts, name="api_dashboard_charts"
    ),
    path(
        "api/dashboard/filters/",
        api.get_dashboard_filters,
        name="api_dashboard_filters",
    ),
    path(
        "api/dashboard/available-years/",
        api.get_executive_available_years,
        name="api_dashboard_available_years",
    ),
    path(
        "api/dashboard/executive-kpis/",
        api.get_executive_dashboard_kpis,
        name="api_executive_dashboard_kpis",
    ),
    path(
        "api/dashboard/fund-status/",
        api.get_executive_fund_status,
        name="api_dashboard_fund_status",
    ),
    path(
        "api/dashboard/performance-metrics/",
        api.get_executive_performance_metrics,
        name="api_dashboard_performance_metrics",
    ),
    path(
        "api/dashboard/monthly-spendings/",
        api.get_executive_monthly_spendings,
        name="api_dashboard_monthly_spendings",
    ),
    path(
        "api/dashboard/executive-alerts/",
        api.get_executive_alerts,
        name="api_dashboard_executive_alerts",
    ),
    path(
        "api/supplier/<int:supplier_id>/",
        api.get_supplier_data,
        name="api_supplier_data",
    ),
    path("api/fund/budget/", api.get_fund_budget, name="api_fund_budget"),
    path("api/mooe/budget/", api.get_mooe_budget, name="api_mooe_budget"),
    path(
        "api/tax-rates/<int:purchase_type_id>/", api.get_tax_rates, name="api_tax_rates"
    ),
    path("api/dashboard-app/", include("dashboard_app.api_urls")),
]
