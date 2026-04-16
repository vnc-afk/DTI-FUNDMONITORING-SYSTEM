"""
Custom decorators for permission-based access control.
"""

from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def regular_user_cannot_edit(view_func):
    """
    Decorator that restricts regular users (non-staff, non-superuser) from
    accessing create, edit, and delete views.

    Only staff and superusers can access these functions.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow staff and superusers
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Deny regular users
        messages.error(
            request,
            "You do not have permission to perform this action. "
            "Only staff members can create, edit, or delete records.",
        )
        return redirect("dashboard")

    return wrapper


def superuser_only(view_func):
    """
    Decorator that restricts access to superusers only.

    Only superusers can access these functions. Staff users are denied.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow only superusers
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Deny staff and regular users
        messages.error(
            request,
            "You do not have permission to perform this action. "
            "Only system administrators can access this feature.",
        )
        return redirect("dashboard")

    return wrapper


def api_login_required(view_func):
    """Allow either Django session auth or JWT auth for API endpoints."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return view_func(request, *args, **kwargs)

        try:
            auth_result = JWTAuthentication().authenticate(request)
        except (AuthenticationFailed, InvalidToken, TokenError) as exc:
            return JsonResponse({"detail": str(exc)}, status=401)

        if auth_result is None:
            return JsonResponse(
                {"detail": "Authentication credentials were not provided."}, status=401
            )

        request.user, request.auth = auth_result
        return view_func(request, *args, **kwargs)

    return wrapper
