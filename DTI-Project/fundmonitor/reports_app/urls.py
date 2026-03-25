from django.urls import path

from . import views

urlpatterns = [
    path('tin/', views.tin, name='tin'),
    path('fund/', views.fund_report, name='fund_report'),
    path('mooe/', views.mooe_report, name='mooe_report'),
    path('nc/', views.nc_report, name='nc_report'),
    path('report/', views.expense_report, name='expense_report'),
    path('mooe/download/<str:report_type>/', views.download_mooe, name='download_mooe'),
    path('fund/download/<str:report_type>/', views.download_fund, name='download_fund'),
]
