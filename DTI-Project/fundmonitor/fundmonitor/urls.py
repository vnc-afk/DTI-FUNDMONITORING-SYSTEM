"""
URL configuration for fundmonitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dashboard_app import views   

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tin/', views.tin, name='tin'),
    path('fund/', views.fund_report, name='fund_report'),
    path('mooe/', views.mooe_report, name='mooe_report'),
    path('nc/', views.nc_report, name='nc_report'),
    path('report/', views.expense_report, name='expense_report'),
    path('', views.dashboard, name='home'),  

    path('bank_statement/', views.bank_statement_list, name='bank_statement_list'),
    path('bank_statement/add/', views.bank_statement_create, name='bank_statement_add'),
    path('bank_statement/edit/<int:pk>/', views.bank_statement_update, name='bank_statement_edit'),
    path('bank_statement/delete/<int:pk>/', views.bank_statement_delete, name='bank_statement_delete'),

    path('fund_sources/', views.fund_sources_view, name='fund_sources'),
    path('fund_sources/add/', views.fund_source_create, name='fund_source_add'),
    path('fund_sources/edit/<int:pk>/', views.fund_source_update, name='fund_source_edit'),
    path('fund_sources/delete/<int:pk>/', views.fund_source_delete, name='fund_source_delete'),
    path('fund_sources/<int:pk>/', views.fund_source_detail, name='fund_source_detail'),
    path('fund_sources/<int:fund_id>/breakdown/add/', views.fund_source_breakdown_add, name='fund_source_breakdown_add'),
    path('fund_sources/breakdown/<int:pk>/edit/', views.fund_source_breakdown_edit, name='fund_source_breakdown_edit'),
    path('fund_sources/breakdown/<int:pk>/delete/', views.fund_source_breakdown_delete, name='fund_source_breakdown_delete'),
    
    path('master_fund_monitoring/', views.master_fund_monitoring_list, name='master_fund_monitoring_list'),
    path('master_fund_monitoring/add/', views.master_fund_monitoring_create, name='master_fund_monitoring_add'),
    path('master_fund_monitoring/edit/<int:pk>/', views.master_fund_monitoring_update, name='master_fund_monitoring_edit'),
    path('master_fund_monitoring/delete/<int:pk>/', views.master_fund_monitoring_delete, name='master_fund_monitoring_delete'),
    path('api/supplier/<int:supplier_id>/', views.get_supplier_data, name='get_supplier_data'),
    
    path('mooe/download/<str:report_type>/', views.download_mooe, name='download_mooe'),
# Staff CRUD
    path('staff/', views.staff_list, name='staff'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:pk>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:pk>/', views.staff_delete, name='staff_delete'),
# Tin CRUD
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/edit/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),
]
