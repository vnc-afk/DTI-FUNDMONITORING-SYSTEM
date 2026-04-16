from django.urls import path

from .api_views import (
    ExpenseReportAPIView,
    FundReportAPIView,
    MooeReportAPIView,
    NcReportAPIView,
    ReportsCatalogAPIView,
    TinReportAPIView,
)

urlpatterns = [
    path("", ReportsCatalogAPIView.as_view(), name="reports_api_catalog"),
    path("expense/", ExpenseReportAPIView.as_view(), name="reports_api_expense"),
    path("mooe/", MooeReportAPIView.as_view(), name="reports_api_mooe"),
    path("nc/", NcReportAPIView.as_view(), name="reports_api_nc"),
    path("fund/", FundReportAPIView.as_view(), name="reports_api_fund"),
    path("tin/", TinReportAPIView.as_view(), name="reports_api_tin"),
]
