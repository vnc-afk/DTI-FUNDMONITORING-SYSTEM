from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrSuperuser(BasePermission):
    """Allow access only to authenticated staff or superuser accounts."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )


class IsAuthenticatedReadOnlyOrStaff(BasePermission):
    """Allow read access to authenticated users; restrict writes to staff/superuser."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(user.is_staff or user.is_superuser)


__all__ = [
    "IsStaffOrSuperuser",
    "IsAuthenticatedReadOnlyOrStaff",
]