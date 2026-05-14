"""
URL configuration for chatbot app.
"""

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot endpoint
    path('api/chatbot/', views.ChatbotAPIView.as_view(), name='chatbot'),

    # Chatbot via function-based view
    path('api/chatbot/message/', views.chatbot_api, name='chatbot_message'),

    # Intent detection test endpoint (for debugging)
    path('api/chatbot/test/intent/', views.ChatIntentTestAPIView.as_view(), name='test_intent'),
]

__all__ = ['urlpatterns']
