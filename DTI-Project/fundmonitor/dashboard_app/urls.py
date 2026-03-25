from django.urls import path

from dashboard_app import views
from dashboard_app.views import archive, api

urlpatterns = [
    # Dashboard
    path('executive-dashboard/', views.executive_dashboard, name='executive_dashboard'),
    path('api/dashboard-data/', views.get_dashboard_data, name='get_dashboard_data'),
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints for caching & AJAX loading
    path('api/dashboard/kpis/', api.get_dashboard_kpis, name='api_dashboard_kpis'),
    path('api/dashboard/charts/', api.get_dashboard_charts, name='api_dashboard_charts'),
    path('api/dashboard/filters/', api.get_dashboard_filters, name='api_dashboard_filters'),
    path('api/supplier/<int:supplier_id>/', api.get_supplier_data, name='api_supplier_data'),
    path('api/fund/budget/', api.get_fund_budget, name='api_fund_budget'),
    path('api/mooe/budget/', api.get_mooe_budget, name='api_mooe_budget'),
    path('api/tax-rates/<int:purchase_type_id>/', api.get_tax_rates, name='api_tax_rates'),

    # Data import (to be moved in later phases)
    path('import/', views.import_data, name='import_data'),
    path('import/result/', views.import_result, name='import_result'),

    # Activity logs (to be moved in later phases)
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('activity-logs/summary/', views.activity_summary, name='activity_summary'),
    path('activity-logs/user/<int:user_id>/', views.user_activity_logs, name='user_activity_logs'),
    path('activity-logs/model/<str:model_name>/', views.model_activity_logs, name='model_activity_logs'),

    # Archive management (to be moved in later phases)
    path('archive/', archive.archive_dashboard, name='archive_dashboard'),
    path('archive/transactions/', archive.archived_transactions, name='archived_transactions'),
    path('archive/statements/', archive.archived_bank_statements, name='archived_statements'),
    path('archive/year/', archive.archive_year, name='archive_year'),
    path('archive/unarchive/', archive.unarchive_year, name='unarchive_year'),
    path('archive/transaction/<int:pk>/unarchive/', archive.unarchive_transaction, name='unarchive_transaction'),
    path('archive/statement/<int:pk>/unarchive/', archive.unarchive_statement, name='unarchive_statement'),
    path('api/archive/stats/', archive.archive_stats_api, name='archive_stats_api'),
]
