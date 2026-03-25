from django.urls import path

from . import views

urlpatterns = [
    # Fund source CRUD
    path('fund_sources/', views.fund_sources_view, name='fund_sources'),
    path('fund_sources/add/', views.fund_source_create, name='fund_source_add'),
    path('fund_sources/edit/<int:pk>/', views.fund_source_update, name='fund_source_edit'),
    path('fund_sources/delete/<int:pk>/', views.fund_source_delete, name='fund_source_delete'),
    path('fund_sources/<int:pk>/', views.fund_source_detail, name='fund_source_detail'),
    path('fund_sources/<int:fund_id>/breakdown/add/', views.fund_source_breakdown_add, name='fund_source_breakdown_add'),
    path('fund_sources/breakdown/<int:pk>/edit/', views.fund_source_breakdown_edit, name='fund_source_breakdown_edit'),
    path('fund_sources/breakdown/<int:pk>/delete/', views.fund_source_breakdown_delete, name='fund_source_breakdown_delete'),

    # Tax table CRUD
    path('tax_table/', views.tax_table_list, name='tax_table'),
    path('tax_table/add/', views.tax_table_create, name='tax_table_add'),
    path('tax_table/edit/<int:pk>/', views.tax_table_update, name='tax_table_edit'),
    path('tax_table/delete/<int:pk>/', views.tax_table_delete, name='tax_table_delete'),

    # Staff CRUD
    path('staff/', views.staff_list, name='staff'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:pk>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:pk>/', views.staff_delete, name='staff_delete'),
    path('staff/bulk_delete/', views.staff_bulk_delete, name='staff_bulk_delete'),

    # Expense object CRUD
    path('expense-objects/', views.expense_object_list, name='expense_object_list'),
    path('expense-objects/add/', views.expense_object_add, name='expense_object_add'),
    path('expense-objects/edit/<int:pk>/', views.expense_object_edit, name='expense_object_edit'),
    path('expense-objects/delete/<int:pk>/', views.expense_object_delete, name='expense_object_delete'),
    path('expense-objects/bulk_delete/', views.expense_object_bulk_delete, name='expense_object_bulk_delete'),

    # Expense category CRUD
    path('expense-categories/', views.expense_category_list, name='expense_category_list'),
    path('expense-categories/add/', views.expense_category_add, name='expense_category_add'),
    path('expense-categories/edit/<int:pk>/', views.expense_category_edit, name='expense_category_edit'),
    path('expense-categories/delete/<int:pk>/', views.expense_category_delete, name='expense_category_delete'),
    path('expense-categories/bulk_delete/', views.expense_category_bulk_delete, name='expense_category_bulk_delete'),

    # Supplier CRUD
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/edit/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),
    path('suppliers/bulk_delete/', views.supplier_bulk_delete, name='supplier_bulk_delete'),

    # Data APIs
    path('api/supplier/<int:supplier_id>/', views.get_supplier_data, name='get_supplier_data'),
    path('api/tax_rates/<int:purchase_type_id>/', views.get_tax_rates, name='get_tax_rates'),
    path('api/fund-budget/', views.get_fund_budget, name='get_fund_budget'),
]
