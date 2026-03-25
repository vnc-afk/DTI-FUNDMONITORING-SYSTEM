from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # User account management
    path('admin/users/', views.user_accounts_list, name='user_accounts_list'),
    path('admin/users/create/', views.user_account_create, name='user_account_create'),
    path('admin/users/<int:user_id>/edit/', views.user_account_edit, name='user_account_edit'),
    path('admin/users/<int:user_id>/detail/', views.user_account_detail, name='user_account_detail'),
    path('admin/users/<int:user_id>/delete/', views.user_account_delete, name='user_account_delete'),
    path('admin/users/<int:user_id>/toggle-status/', views.user_account_toggle_status, name='user_account_toggle_status'),
    path('admin/users/<int:user_id>/reset-password/', views.user_account_reset_password, name='user_account_reset_password'),
    path('api/user-accounts/data/', views.api_user_accounts_data, name='api_user_accounts_data'),
    path('change-password/', views.change_initial_password, name='change_initial_password'),

    # Authentication
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # User settings and notifications
    path('settings/', views.user_settings, name='user_settings'),
    path('api/update-theme/', views.api_update_theme, name='api_update_theme'),
    path('api/change-password/', views.api_change_password, name='api_change_password'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/read-all/', views.api_notifications_mark_all_read, name='api_notifications_mark_all_read'),
    path('api/notifications/<int:notification_id>/read/', views.api_notification_mark_read, name='api_notification_mark_read'),
]
