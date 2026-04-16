import secrets
import string

from django.contrib.auth.models import User
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import UserPreference
from .serializers import UserAccountSerializer, UserPreferenceSerializer


class UserAccountViewSet(viewsets.ModelViewSet):
    serializer_class = UserAccountSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("-date_joined")

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        new_password = "".join(secrets.choice(alphabet) for _ in range(12))

        user.set_password(new_password)
        user.save(update_fields=["password"])

        preference, created = UserPreference.objects.get_or_create(user=user)
        if not created:
            preference.password_changed = False
            preference.save(update_fields=["password_changed", "updated_at"])

        return Response(
            {
                "message": "Password reset successfully.",
            },
            status=status.HTTP_200_OK,
        )


class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


__all__ = [
    "UserAccountViewSet",
    "UserPreferenceViewSet",
]
