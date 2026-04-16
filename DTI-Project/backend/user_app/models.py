from django.contrib.auth.models import User
from django.db import models


class UserPreference(models.Model):
    """Store user settings and preferences."""

    THEME_CHOICES = [
        ("dark", "Dark Theme"),
        ("light", "Light Theme"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preference"
    )
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="dark")
    notifications_enabled = models.BooleanField(default=True)
    items_per_page = models.IntegerField(default=25)
    password_changed = models.BooleanField(
        default=False, help_text="Whether user has changed their initial password"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_userpreference"

    def __str__(self):
        return f"{self.user.username}'s Preferences"


__all__ = ["UserPreference"]
