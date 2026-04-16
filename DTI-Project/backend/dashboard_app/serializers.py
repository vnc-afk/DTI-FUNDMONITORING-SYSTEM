from rest_framework import serializers

from .models import ActivityLog, Notification


class ActivityLogSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_is_superuser = serializers.SerializerMethodField()
    user_is_staff = serializers.SerializerMethodField()
    user_groups = serializers.SerializerMethodField()
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    formatted_timestamp = serializers.CharField(
        source="get_formatted_timestamp", read_only=True
    )

    def get_user_full_name(self, obj):
        if not obj.user:
            return "Unknown"
        full_name = (obj.user.get_full_name() or "").strip()
        return full_name or obj.user.username

    def get_user_username(self, obj):
        return obj.user.username if obj.user else ""

    def get_user_is_superuser(self, obj):
        return bool(obj.user and obj.user.is_superuser)

    def get_user_is_staff(self, obj):
        return bool(obj.user and obj.user.is_staff)

    def get_user_groups(self, obj):
        if not obj.user:
            return []
        return list(obj.user.groups.values_list("name", flat=True))

    class Meta:
        model = ActivityLog
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


__all__ = [
    "ActivityLogSerializer",
    "NotificationSerializer",
]
