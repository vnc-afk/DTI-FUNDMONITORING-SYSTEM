"""API compatibility wrappers for data_management_app."""

from dashboard_app.views.api import get_fund_budget, get_supplier_data, get_tax_rates

__all__ = [
    "get_supplier_data",
    "get_tax_rates",
    "get_fund_budget",
]
