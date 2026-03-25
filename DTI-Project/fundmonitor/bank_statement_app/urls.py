from django.urls import path

from . import views

urlpatterns = [
    path('bank_statement/', views.bank_statement_list, name='bank_statement_list'),
    path('bank_statement/add/', views.bank_statement_create, name='bank_statement_add'),
    path('bank_statement/edit/<int:pk>/', views.bank_statement_update, name='bank_statement_edit'),
    path('bank_statement/delete/<int:pk>/', views.bank_statement_delete, name='bank_statement_delete'),
    path('bank_statement/<int:pk>/update_status/', views.bank_statement_update_status, name='bank_statement_update_status'),
    path('bank_statement/bulk_delete/', views.bank_statement_bulk_delete, name='bank_statement_bulk_delete'),
]
