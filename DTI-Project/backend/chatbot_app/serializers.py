"""
Serializers for chatbot API endpoints.
"""

from rest_framework import serializers
from .models import ChatHistory


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for incoming chat messages."""

    message = serializers.CharField(
        max_length=1000,
        min_length=1,
        help_text="User's question or query"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chatbot response."""

    intent = serializers.CharField(
        max_length=50,
        help_text="Detected intent"
    )
    confidence = serializers.FloatField(
        help_text="Confidence score of intent detection (0-1)"
    )
    response = serializers.CharField(
        help_text="Chatbot's response"
    )
    message_cleaned = serializers.CharField(
        help_text="Cleaned version of user message"
    )
    timestamp = serializers.DateTimeField(
        required=False,
        help_text="When the response was generated"
    )


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for chat history records."""

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = ChatHistory
        fields = [
            'id',
            'user',
            'user_display',
            'message',
            'detected_intent',
            'confidence_score',
            'response',
            'timestamp',
            'is_resolved',
        ]
        read_only_fields = ['id', 'timestamp']

    def get_user_display(self, obj):
        """Get user display name."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "Anonymous"


__all__ = ['ChatMessageSerializer', 'ChatResponseSerializer', 'ChatHistorySerializer']
