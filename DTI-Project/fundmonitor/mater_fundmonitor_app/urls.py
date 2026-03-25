from django.urls import path

from . import views

urlpatterns = [
    # Master fund monitoring
    path('master_fund_monitoring/', views.master_fund_monitoring_list, name='master_fund_monitoring_list'),
    path('master_fund_monitoring/add/', views.master_fund_monitoring_create, name='master_fund_monitoring_add'),
    path('master_fund_monitoring/edit/<int:pk>/', views.master_fund_monitoring_update, name='master_fund_monitoring_edit'),
    path('master_fund_monitoring/delete/<int:pk>/', views.master_fund_monitoring_delete, name='master_fund_monitoring_delete'),
    path('master_fund_monitoring/bulk_delete/', views.master_fund_monitoring_bulk_delete, name='master_fund_monitoring_bulk_delete'),

    # Monitoring APIs
    path('api/mooe-budget/', views.get_mooe_budget, name='get_mooe_budget'),
]
