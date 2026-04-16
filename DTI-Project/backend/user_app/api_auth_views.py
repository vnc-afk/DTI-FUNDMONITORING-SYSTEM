from django.contrib.auth.models import User
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .forms import InitialPasswordChangeForm
from .models import UserPreference


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserPreference.objects.get_or_create(user=user)
        return user


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class FundMonitorTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["groups"] = list(user.groups.values_list("name", flat=True))
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        preference, _ = UserPreference.objects.get_or_create(user=user)
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "groups": list(user.groups.values_list("name", flat=True)),
            "force_password_change": not preference.password_changed,
        }
        return data


class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FundMonitorTokenObtainPairSerializer


class ProtectedProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        preference, _ = UserPreference.objects.get_or_create(user=user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "force_password_change": not preference.password_changed,
                "roles": {
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "groups": list(user.groups.values_list("name", flat=True)),
                },
            },
            status=status.HTTP_200_OK,
        )


class InitialPasswordChangeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        preference, _ = UserPreference.objects.get_or_create(user=request.user)
        requires_change = not preference.password_changed

        return Response(
            {
                "force_change": requires_change,
                "title": "Change Your Password",
                "subtitle": (
                    "You must change your temporary password before continuing"
                    if requires_change
                    else "Update your account password to keep it secure"
                ),
                "new_password_help_text": "Must contain uppercase, lowercase, numbers. At least 8 characters.",
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        preference, _ = UserPreference.objects.get_or_create(user=request.user)

        if preference.password_changed:
            return Response(
                {
                    "success": False,
                    "message": "Initial password has already been changed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = InitialPasswordChangeForm(request.user, request.data)
        if form.is_valid():
            form.save()
            return Response(
                {
                    "success": True,
                    "message": "Password changed successfully.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": form.errors,
                "non_field_errors": form.non_field_errors(),
                "message": "Please fix the errors below.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class AdminOnlyExampleAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response(
            {
                "message": "Admin-only route accessed successfully.",
                "user": request.user.username,
            },
            status=status.HTTP_200_OK,
        )


__all__ = [
    "RegisterAPIView",
    "LoginAPIView",
    "ProtectedProfileAPIView",
    "InitialPasswordChangeAPIView",
    "AdminOnlyExampleAPIView",
]
