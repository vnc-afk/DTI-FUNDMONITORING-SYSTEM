/**
 * Chatbot Composable
 * Provides reactive chatbot functionality for components
 */

import { ref, computed, watch } from 'vue'
import { useChatbotStore } from '@/stores/chatbotStore'

export function useChatbot() {
  const store = useChatbotStore()
  const inputMessage = ref('')
  const isScrolling = ref(false)
  const showClearModal = ref(false)

  // Computed properties from store
  const messages = computed(() => store.messages)
  const isLoading = computed(() => store.isLoading)
  const error = computed(() => store.error)
  const isOpen = computed(() => store.isOpen)
  const hasMessages = computed(() => store.hasMessages)
  const messageCount = computed(() => store.messageCount)

  // Watch for new messages to scroll to bottom
  watch(
    () => store.messages.length,
    () => {
      // Scroll to bottom on next tick
      setTimeout(() => {
        const messageContainers = [
          document.querySelector('[data-testid="chatbot-messages"]'),
          document.querySelector('.messages-area'),
          document.querySelector('.chatbot-messages'),
        ].filter(Boolean)

        for (const messagesContainer of messageContainers) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight
        }
      }, 0)
    }
  )

  // Methods
  async function handleSendMessage() {
    if (!inputMessage.value.trim() || isLoading.value) {
      return
    }

    const message = inputMessage.value
    inputMessage.value = '' // Clear input immediately

    await store.sendMessage(message)
  }

  function handleClear() {
    showClearModal.value = true
  }

  function confirmClearMessages() {
    store.clearMessages()
    inputMessage.value = ''
    showClearModal.value = false
  }

  function cancelClearMessages() {
    showClearModal.value = false
  }

  function toggleChatbot() {
    store.toggleChatbot()
  }

  function closeChatbot() {
    store.closeChatbot()
  }

  function openChatbot() {
    store.openChatbot()
  }

  // Handle Enter key
  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  // Format message time
  function formatTime(timestamp) {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Format message content (handle newlines, etc)
  function formatMessageContent(content) {
    return content
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
  }

  return {
    // State
    inputMessage,
    isScrolling,
    showClearModal,

    // Computed
    messages,
    isLoading,
    error,
    isOpen,
    hasMessages,
    messageCount,

    // Methods
    handleSendMessage,
    handleClear,
    confirmClearMessages,
    cancelClearMessages,
    toggleChatbot,
    closeChatbot,
    openChatbot,
    handleKeydown,
    formatTime,
    formatMessageContent,
  }
}

export default useChatbot
