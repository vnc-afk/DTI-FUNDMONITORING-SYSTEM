"""
Middleware for dashboard_app
Handles password change enforcement and user context capture for signals
"""

import threading

from django.shortcuts import redirect
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from user_app.models import UserPreference

# Thread-local storage for current user
_current_user = threading.local()


class ForcePasswordChangeMiddleware:
    """
    Middleware that forces users with unchanged temporary passwords to change them.
    Redirects to change password page on first login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for anonymous users
        if not request.user.is_authenticated:
            return None

        # Check if current URL is exempt
        if self._is_url_exempt(request.path):
            return None

        # Skip if user has changed password
        try:
            pref = UserPreference.objects.get(user=request.user)
            if pref.password_changed:
                return None  # Password already changed, allow access
        except UserPreference.DoesNotExist:
            # Create preference with password not changed
            UserPreference.objects.create(user=request.user, password_changed=False)

        # User hasn't changed password, redirect to change password page
        return redirect("change_initial_password")

    def _is_url_exempt(self, path):
        """Check if URL is exempt from password change requirement"""
        # Exempt paths - no need to use reverse()
        exempt_paths = [
            "/accounts/login/",
            "/accounts/logout/",
            "/admin/logout/",
            "/change-password/",
            "/api/",
            "/static/",
            "/media/",
        ]

        # Check if path matches any exempt path
        for exempt_path in exempt_paths:
            if path == exempt_path or path.startswith(exempt_path):
                return True

        return False


class CurrentUserMiddleware:
    """
    Middleware to store the current user in thread-local storage.
    This allows signals to access the user who made the change.
    Required for activity logging in signals.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store session-authenticated user first.
        current_user = request.user

        # For API requests authenticated via JWT, request.user can still be
        # anonymous at middleware time. Resolve bearer token explicitly so
        # save/delete signals can attribute actions and create notifications.
        if not getattr(current_user, "is_authenticated", False):
            try:
                auth_result = JWTAuthentication().authenticate(request)
                if auth_result is not None:
                    current_user, _ = auth_result
            except (AuthenticationFailed, InvalidToken, TokenError):
                current_user = request.user

        _current_user.user = current_user

        try:
            # Call the main request handler
            response = self.get_response(request)
        finally:
            # Clean up thread-local storage
            if hasattr(_current_user, "user"):
                del _current_user.user

        return response


def get_current_user():
    """Get the current user from thread-local storage"""
    return getattr(_current_user, "user", None)
