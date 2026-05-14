"""
API views for chatbot functionality.
"""

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone

from .chatbot_service import ChatbotService
from .serializers import (
    ChatMessageSerializer,
    ChatResponseSerializer,
)

logger = logging.getLogger(__name__)


def _handle_chatbot_request(request):
    """Shared chatbot request handler for function and class based views."""
    # Validate input
    serializer = ChatMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'error': 'Invalid message format',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    message = serializer.validated_data['message']

    try:
        # Process message
        result = ChatbotService.process_message(message, request.user if request.user.is_authenticated else None)

        # Add timestamp
        result['timestamp'] = timezone.now()

        # Validate response
        response_serializer = ChatResponseSerializer(result)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                'error': 'Internal server error',
                'details': str(e),
                'response': 'Sorry, I encountered an error processing your request. Please try again.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anonymous users, or change to IsAuthenticated
def chatbot_api(request):
    """
    Main chatbot API endpoint.

    POST /api/chatbot/
    Input: { "message": "user question" }
    Output: { "intent": "...", "confidence": 0.8, "response": "...", ... }

    Args:
        request: HTTP request containing user message

    Returns:
        JSON response with chatbot reply and metadata
    """
    return _handle_chatbot_request(request)


class ChatbotAPIView(APIView):
    """
    Class-based view for chatbot API.

    Supports:
    - POST: Send message and get response
    - GET: Get chat history (if authenticated)
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests to send chat messages.

        Args:
            request: HTTP request with message

        Returns:
            JSON response with chatbot reply
        """
        return _handle_chatbot_request(request)


class ChatIntentTestAPIView(APIView):
    """
    Test endpoint for intent detection.

    Useful for debugging and testing intent detection logic.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Test intent detection without generating a response.

        Args:
            request: HTTP request with message

        Returns:
            JSON with detected intent and confidence
        """
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid message format',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        message = serializer.validated_data['message']

        try:
            intent, confidence = ChatbotService.detect_intent(message)
            cleaned = ChatbotService.clean_message(message)

            return Response(
                {
                    'message': message,
                    'message_cleaned': cleaned,
                    'detected_intent': intent,
                    'confidence': confidence,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


__all__ = ['chatbot_api', 'ChatbotAPIView', 'ChatIntentTestAPIView']
