from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserPreference


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=True
    )

    def validate_username(self, value):
        username = (value or "").strip()
        if len(username) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        return username

    def validate_password(self, value):
        password = (value or "").strip()

        if not password:
            return ""

        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)

        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not (has_upper and has_lower and has_digit):
            raise serializers.ValidationError(
                "Password must contain uppercase letters, lowercase letters, and numbers."
            )

        return password

    def create(self, validated_data):
        password = validated_data.pop("password", "").strip()
        fixed_temporary_password = "TempPass123!"

        user = User(**validated_data)
        user.is_active = True

        if password:
            user.set_password(password)
        else:
            user.set_password(fixed_temporary_password)

        user.save()

        preference, created = UserPreference.objects.get_or_create(user=user)
        if not created:
            preference.password_changed = False
            preference.save(update_fields=["password_changed", "updated_at"])

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "").strip()

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["date_joined", "last_login"]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


__all__ = [
    "UserAccountSerializer",
    "UserPreferenceSerializer",
]
