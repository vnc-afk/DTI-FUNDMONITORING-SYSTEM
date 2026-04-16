"""Utility helpers for user preference driven behavior."""

from user_app.models import UserPreference


def get_items_per_page(request, default=25):
    """Return the authenticated user's preferred page size, with safe fallback."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return default

    try:
        page_size = int(
            UserPreference.objects.only("items_per_page").get(user=user).items_per_page
        )
    except (UserPreference.DoesNotExist, TypeError, ValueError):
        return default

    return page_size if page_size > 0 else default


def notifications_enabled_for_user(user, default=True):
    """Return whether notifications are enabled for a given authenticated user."""
    if not user or not user.is_authenticated:
        return False

    try:
        return bool(
            UserPreference.objects.only("notifications_enabled")
            .get(user=user)
            .notifications_enabled
        )
    except UserPreference.DoesNotExist:
        return default


def notifications_enabled_for_request(request, default=True):
    """Return whether notifications are enabled for the current request user."""
    return notifications_enabled_for_user(
        getattr(request, "user", None), default=default
    )
