from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    # Authentication
    path("accounts/login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    path(
        "change-password/",
        views.change_initial_password,
        name="change_initial_password",
    ),
    # User settings and notifications APIs
    path("api/change-password/", views.api_change_password, name="api_change_password"),
    path("api/notifications/", views.api_notifications, name="api_notifications"),
    path(
        "api/notifications/read-all/",
        views.api_notifications_mark_all_read,
        name="api_notifications_mark_all_read",
    ),
    path(
        "api/notifications/<int:notification_id>/read/",
        views.api_notification_mark_read,
        name="api_notification_mark_read",
    ),
    path("api/user-app/", include("user_app.api_urls")),
]
