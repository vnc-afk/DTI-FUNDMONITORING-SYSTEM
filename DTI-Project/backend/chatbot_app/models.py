from django.contrib.auth.models import User
from django.db import models


class ChatHistory(models.Model):
    """Store chat interactions for auditing and learning purposes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_histories",
        null=True,
        blank=True
    )
    message = models.TextField(
        help_text="User's question/message"
    )
    detected_intent = models.CharField(
        max_length=50,
        blank=True,
        help_text="Detected intent from message processing"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence score for intent detection (0-1)"
    )
    response = models.TextField(
        help_text="Chatbot's response"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    is_resolved = models.BooleanField(
        default=True,
        help_text="Whether the response satisfied the user's query"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['detected_intent', '-timestamp']),
        ]
        verbose_name = "Chat History"
        verbose_name_plural = "Chat Histories"

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def get_formatted_timestamp(self):
        """Return human-readable timestamp."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")


__all__ = ['ChatHistory']
