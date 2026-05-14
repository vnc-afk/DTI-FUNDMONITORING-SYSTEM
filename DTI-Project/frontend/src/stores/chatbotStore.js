/**
 * Chatbot Store (Pinia)
 * Manages chatbot state and messages
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import chatbotService from '@/services/chatbotService'

export const useChatbotStore = defineStore('chatbot', () => {
  // State
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const isOpen = ref(false)

  // Computed
  const messageCount = computed(() => messages.value.length)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])
  const hasMessages = computed(() => messages.value.length > 0)

  // Actions - Messages
  async function sendMessage(userMessage) {
    if (!userMessage.trim()) {
      error.value = 'Please enter a message'
      return null
    }

    // Add user message to chat
    const userMsg = {
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
      id: `user-${Date.now()}`,
    }
    messages.value.push(userMsg)

    isLoading.value = true
    error.value = null

    try {
      const response = await chatbotService.sendMessage(userMessage)

      // Add bot response to chat
      const botMsg = {
        type: 'bot',
        content: response.response,
        intent: response.intent,
        confidence: response.confidence,
        timestamp: new Date(response.timestamp),
        id: `bot-${Date.now()}`,
      }
      messages.value.push(botMsg)

      return response
    } catch (err) {
      error.value = err.message || 'Failed to get response from chatbot'

      // Add error message
      const errorMsg = {
        type: 'error',
        content: error.value,
        timestamp: new Date(),
        id: `error-${Date.now()}`,
      }
      messages.value.push(errorMsg)

      return null
    } finally {
      isLoading.value = false
    }
  }

  // Add message directly (useful for system messages)
  function addMessage(content, type = 'bot', metadata = {}) {
    const message = {
      type,
      content,
      timestamp: new Date(),
      id: `${type}-${Date.now()}`,
      ...metadata,
    }
    messages.value.push(message)
    return message
  }

  // Clear all messages
  function clearMessages() {
    messages.value = []
    error.value = null
  }

  // Actions - UI
  function toggleChatbot() {
    isOpen.value = !isOpen.value
  }

  function openChatbot() {
    isOpen.value = true
  }

  function closeChatbot() {
    isOpen.value = false
  }

  // Helper functions
  function getMessagesByType(type) {
    return messages.value.filter((msg) => msg.type === type)
  }

  function getMessageById(id) {
    return messages.value.find((msg) => msg.id === id)
  }

  function hasError() {
    return error.value !== null
  }

  return {
    // State
    messages,
    isLoading,
    error,
    isOpen,

    // Computed
    messageCount,
    lastMessage,
    hasMessages,

    // Actions - Messages
    sendMessage,
    addMessage,
    clearMessages,

    // Actions - UI
    toggleChatbot,
    openChatbot,
    closeChatbot,

    // Helpers
    getMessagesByType,
    getMessageById,
    hasError,
  }
})

export default useChatbotStore
