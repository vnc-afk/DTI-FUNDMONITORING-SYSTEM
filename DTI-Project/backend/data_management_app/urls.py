from django.urls import include, path

from . import views

urlpatterns = [
    # Data APIs
    path(
        "api/supplier/<int:supplier_id>/",
        views.get_supplier_data,
        name="get_supplier_data",
    ),
    path(
        "api/tax_rates/<int:purchase_type_id>/",
        views.get_tax_rates,
        name="get_tax_rates",
    ),
    path("api/fund-budget/", views.get_fund_budget, name="get_fund_budget"),
    path("api/data-management-app/", include("data_management_app.api_urls")),
]
