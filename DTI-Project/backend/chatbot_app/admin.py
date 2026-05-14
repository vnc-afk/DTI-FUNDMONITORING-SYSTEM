"""
Admin configuration for chatbot app.
"""

from django.contrib import admin
from .models import ChatHistory


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    """Admin interface for ChatHistory model."""

    list_display = [
        'get_user_display',
        'detected_intent',
        'confidence_score',
        'timestamp',
        'is_resolved',
    ]
    list_filter = [
        'detected_intent',
        'is_resolved',
        'timestamp',
    ]
    search_fields = [
        'user__username',
        'message',
        'response',
        'detected_intent',
    ]
    readonly_fields = [
        'timestamp',
        'message',
        'response',
        'detected_intent',
        'confidence_score',
    ]
    ordering = ['-timestamp']

    fieldsets = (
        ('User & Message', {
            'fields': ('user', 'message')
        }),
        ('Detection', {
            'fields': ('detected_intent', 'confidence_score')
        }),
        ('Response', {
            'fields': ('response', 'is_resolved')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

    def get_user_display(self, obj):
        """Display user name or 'Anonymous'."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "Anonymous"

    get_user_display.short_description = "User"

    def has_add_permission(self, request):
        """Disable manual addition via admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of chat history."""
        return request.user.is_superuser


__all__ = ['ChatHistoryAdmin']
