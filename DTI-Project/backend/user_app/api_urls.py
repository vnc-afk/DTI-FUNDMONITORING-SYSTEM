from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .api_auth_views import (
    AdminOnlyExampleAPIView,
    InitialPasswordChangeAPIView,
    LoginAPIView,
    ProtectedProfileAPIView,
    RegisterAPIView,
)
from .api_views import UserAccountViewSet, UserPreferenceViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register("accounts", UserAccountViewSet, basename="user-account")
router.register("preferences", UserPreferenceViewSet, basename="user-preference")

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="api_auth_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_auth_refresh"),
    path("auth/register/", RegisterAPIView.as_view(), name="api_auth_register"),
    path("auth/profile/", ProtectedProfileAPIView.as_view(), name="api_auth_profile"),
    path(
        "auth/initial-password/",
        InitialPasswordChangeAPIView.as_view(),
        name="api_auth_initial_password",
    ),
    path(
        "auth/admin-only/",
        AdminOnlyExampleAPIView.as_view(),
        name="api_auth_admin_only",
    ),
]

urlpatterns += router.urls
