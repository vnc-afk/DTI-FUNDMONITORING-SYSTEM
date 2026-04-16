from django.urls import path

from . import views

urlpatterns = [
    path(
        "api/bank_statement/",
        views.BankStatementListCreateAPIView.as_view(),
        name="bank_statement_list",
    ),
    path(
        "api/bank_statement/<int:pk>/",
        views.BankStatementDetailAPIView.as_view(),
        name="bank_statement_detail",
    ),
    path(
        "api/bank_statement/<int:pk>/update_status/",
        views.BankStatementStatusUpdateAPIView.as_view(),
        name="bank_statement_update_status",
    ),
    path(
        "api/bank_statement/bulk_delete/",
        views.BankStatementBulkDeleteAPIView.as_view(),
        name="bank_statement_bulk_delete",
    ),
]
