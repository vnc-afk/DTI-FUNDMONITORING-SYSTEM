"""Notification model for in-app financial alerts and reminders."""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """Database-backed notification entry for dashboard alerts."""

    LEVEL_INFO = "info"
    LEVEL_SUCCESS = "success"
    LEVEL_WARNING = "warning"
    LEVEL_CRITICAL = "critical"

    LEVEL_CHOICES = [
        (LEVEL_INFO, "Info"),
        (LEVEL_SUCCESS, "Success"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_CRITICAL, "Critical"),
    ]

    CATEGORY_BUDGET = "budget"
    CATEGORY_EXPENSE = "expense"
    CATEGORY_FUND = "fund"
    CATEGORY_DEADLINE = "deadline"
    CATEGORY_SYSTEM = "system"
    CATEGORY_FINANCE = "finance"
    CATEGORY_FINANCIAL_ANALYSIS = "financial_analysis"
    CATEGORY_FINANCE_MONITORING = "finance_monitoring"
    CATEGORY_FUND_BUDGET = "fund_budget"

    CATEGORY_CHOICES = [
        (CATEGORY_BUDGET, "Budget"),
        (CATEGORY_EXPENSE, "Expense"),
        (CATEGORY_FUND, "Fund"),
        (CATEGORY_DEADLINE, "Deadline"),
        (CATEGORY_SYSTEM, "System"),
        (CATEGORY_FINANCE, "Finance"),
        (CATEGORY_FINANCIAL_ANALYSIS, "Financial Analysis"),
        (CATEGORY_FINANCE_MONITORING, "Finance Monitoring"),
        (CATEGORY_FUND_BUDGET, "Fund/Budget"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Notification recipient",
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_notifications",
        help_text="User who triggered the notification",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INFO)
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_SYSTEM
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    event_key = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        db_index=True,
        help_text="Optional deduplication key for recurring alerts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["event_key", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def get_created_at_local(self):
        if not self.created_at:
            return None
        return timezone.localtime(self.created_at)

    def get_read_at_local(self):
        if not self.read_at:
            return None
        return timezone.localtime(self.read_at)

    def get_created_display(self):
        created_at_local = self.get_created_at_local()
        if not created_at_local:
            return ""
        return created_at_local.strftime("%b %d, %Y %I:%M %p")

    def get_read_display(self):
        read_at_local = self.get_read_at_local()
        if not read_at_local:
            return ""
        return read_at_local.strftime("%b %d, %Y %I:%M %p")

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.localtime()
            self.save(update_fields=["is_read", "read_at"])
