/**
 * Chatbot Widget Component
 * Displays the chatbot interface with input and quick prompts
 */

<template>
  <div class="chatbot-widget" :class="{ open: isOpen }">
    <!-- Header -->
    <div class="chatbot-header">
      <div class="chatbot-title">
        <MessageCircle class="icon" aria-hidden="true" />
        <h3>Fund Monitor Assistant</h3>
      </div>
      <div class="header-actions">
        <button class="btn-icon" @click="toggleSuggestions" title="Suggested questions" aria-label="Suggested questions">
          <HelpCircle aria-hidden="true" />
        </button>
        <button
          v-if="hasMessages"
          class="btn-icon"
          @click="handleClear"
          title="Clear chat"
          aria-label="Clear messages"
        >
          <Trash2 aria-hidden="true" />
        </button>
        <button
          class="btn-close"
          @click="closeChatbot"
          title="Close"
          aria-label="Close chatbot"
        >
          <X aria-hidden="true" />
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div class="chatbot-messages" data-testid="chatbot-messages">
      <div v-if="showSuggestions" ref="suggestionsPanel" class="suggestions-panel">
        <div class="suggestions-header">
          <strong>Suggested questions</strong>
          <button class="btn-link" @click="toggleSuggestions">Close</button>
        </div>
        <div class="suggestions-list">
          <button
            v-for="(q, idx) in suggestions"
            :key="idx"
            class="suggestion-item"
            @click="selectSuggestion(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <div v-if="!hasMessages" class="empty-state">
        <p class="greeting">
          <Hand class="greeting-icon" aria-hidden="true" />
          <span>Welcome to Fund Monitor Assistant!</span>
        </p>
        <p class="subtitle">Ask me about your funds, expenses, suppliers, or reports.</p>
        <div class="quick-prompts">
          <button
            class="prompt-btn"
            @click="() => (inputMessage = 'What are the total funds?')"
          >
            Total Funds
          </button>
          <button
            class="prompt-btn"
            @click="() => (inputMessage = 'Show me top expenses')"
          >
            Top Expenses
          </button>
          <button
            class="prompt-btn"
            @click="() => (inputMessage = 'Financial summary')"
          >
            Financial Summary
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="[`message-${message.type}`, { loading: isLoading && message === messages[messages.length - 1] }]"
      >
        <!-- User Message -->
        <div v-if="message.type === 'user'" class="message-user">
          <div class="message-content user-content">
            {{ message.content }}
          </div>
          <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        </div>

        <!-- Bot Message -->
        <div v-else-if="message.type === 'bot'" class="message-bot">
          <div class="message-avatar">
            <Bot aria-hidden="true" />
          </div>
          <div class="message-body">
            <div class="message-content bot-content">
              <div v-for="(line, idx) in formatMessageContent(message.content)" :key="idx">
                {{ line }}
              </div>
            </div>
            <div class="message-meta">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              <span
                v-if="message.intent !== 'unknown'"
                class="intent-badge"
                :title="`Confidence: ${(message.confidence * 100).toFixed(0)}%`"
              >
                {{ message.intent }} ({{ (message.confidence * 100).toFixed(0) }}%)
              </span>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-else-if="message.type === 'error'" class="message-error">
          <div class="error-icon">
            <AlertTriangle aria-hidden="true" />
          </div>
          <div class="error-content">
            {{ message.content }}
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="message message-loading">
        <div class="message-avatar">
          <Bot aria-hidden="true" />
        </div>
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chatbot-input">
      <textarea
        v-model="inputMessage"
        class="message-input"
        placeholder="Ask me anything about funds, expenses, suppliers..."
        @keydown="handleKeydown"
        :disabled="isLoading"
        rows="1"
      ></textarea>
      <button
        class="btn-send"
        @click="handleSendMessage"
        :disabled="isLoading || !inputMessage.trim()"
        :aria-label="isLoading ? 'Sending...' : 'Send message'"
      >
        <Send v-if="!isLoading" aria-hidden="true" />
        <span v-else class="spinner"></span>
      </button>
    </div>

    <!-- Info Text -->
    <div class="chatbot-footer">
      <small>Powered by Fund Monitor AI</small>
    </div>
  </div>

    <div v-if="showClearModal" class="modal-backdrop" @click.self="cancelClearMessages">
      <div class="clear-modal" role="alertdialog" aria-modal="true" aria-labelledby="clear-modal-title">
        <div class="clear-modal-header">
          <div class="clear-modal-icon" aria-hidden="true">
            <AlertTriangle />
          </div>
          <h4 id="clear-modal-title">Clear chat history?</h4>
        </div>
        <p class="clear-modal-body">
          This will remove all messages from the current conversation.
        </p>
        <div class="clear-modal-actions">
          <button class="btn btn-secondary" @click="cancelClearMessages">Cancel</button>
          <button class="btn btn-danger" @click="confirmClearMessages">Clear Chat</button>
        </div>
      </div>
    </div>

  <!-- Toggle Button (when closed) -->
  <button
    v-if="!isOpen"
    class="chatbot-toggle"
    @click="toggleChatbot"
    :aria-label="messageCount > 0 ? `Chatbot (${messageCount})` : 'Open chatbot'"
  >
    <MessageCircle class="toggle-icon" aria-hidden="true" />
    <span v-if="messageCount > 0" class="message-badge">{{ messageCount }}</span>
  </button>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { AlertTriangle, Bot, Hand, HelpCircle, MessageCircle, Send, Trash2, X } from 'lucide-vue-next'
import { useChatbot } from '@/composables/useChatbot'

const {
  inputMessage,
  messages,
  isLoading,
  error,
  isOpen,
  hasMessages,
  messageCount,
  showClearModal,
  handleSendMessage,
  handleClear,
  confirmClearMessages,
  cancelClearMessages,
  toggleChatbot,
  closeChatbot,
  handleKeydown,
  formatTime,
  formatMessageContent,
} = useChatbot()

const showSuggestions = ref(false)
const suggestionsPanel = ref(null)
const suggestions = [
  "What's my total available funds?",
  'Show fund allocation by source',
  'How much was spent today?',
  'Expenses this week',
  "Give me this month's summary",
  'Top 5 highest expenses',
  'List all suppliers',
  'Who is the top supplier?',
  'Show unreconciled transactions',
  'Bank reconciliation status',
  'Overall financial summary',
  'Show user activity stats',
]

function toggleSuggestions() {
  showSuggestions.value = !showSuggestions.value

  if (showSuggestions.value) {
    nextTick(() => {
      suggestionsPanel.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

async function selectSuggestion(question) {
  inputMessage.value = question
  showSuggestions.value = false
  await handleSendMessage()
}
</script>

<style scoped lang="scss">
// Variables
$primary-color: var(--brand-navy-700);
$primary-dark: var(--brand-navy-600);
$warning-color: var(--status-warning-text);
$danger-color: var(--status-danger-text);
$light-gray: var(--surface-page);
$border-color: var(--border-default);
$text-color: var(--text-primary);
$text-light: var(--text-tertiary);
$surface-base: var(--surface-base);
$surface-subtle: var(--surface-subtle);

// Widget Container
.chatbot-widget {
  position: fixed;
  right: var(--space-5);
  bottom: var(--space-5);
  width: min(420px, calc(100vw - 2rem));
  max-height: min(720px, calc(100vh - 2rem));
  opacity: 0;
  pointer-events: none;
  transform: translateY(14px) scale(0.98);
  transition:
    opacity var(--duration-normal) var(--ease-out),
    transform var(--duration-normal) var(--ease-out),
    box-shadow var(--duration-normal) var(--ease-out);
  z-index: var(--z-overlay);
  box-shadow: var(--shadow-xl);
  border-radius: var(--radius-2xl);
  overflow: hidden;
  background: color-mix(in srgb, var(--surface-base) 96%, transparent);
  backdrop-filter: blur(14px);
  border: 1px solid var(--border-subtle);

  &.open {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0) scale(1);
    display: flex;
    flex-direction: column;
  }

  @media (max-width: 640px) {
    right: var(--space-4);
    bottom: var(--space-4);
    width: calc(100vw - 2rem);
    max-height: calc(100vh - 2rem);
  }

  @media (max-width: 520px) {
    inset: 0;
    width: 100vw;
    max-height: 100vh;
    border-radius: 0;
    transform: none;
  }
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: color-mix(in srgb, var(--surface-page) 72%, transparent);
  backdrop-filter: blur(10px);
}

.clear-modal {
  width: min(100%, 360px);
  overflow: hidden;
  border-radius: var(--radius-2xl);
  border: 1px solid var(--border-subtle);
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--surface-base) 94%, var(--brand-navy-50) 6%) 0%,
    var(--surface-base) 100%
  );
  box-shadow: var(--shadow-2xl);
}

.clear-modal-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5) var(--space-3);
}

.clear-modal-icon {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: var(--status-danger-text);
  background: var(--status-danger-bg);
  border: 1px solid var(--status-danger-border);
  flex: 0 0 auto;
}

.clear-modal-header h4 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.clear-modal-body {
  margin: 0;
  padding: 0 var(--space-5);
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.clear-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-5);
  padding: var(--space-4) var(--space-5) var(--space-5);
}

// Header
.chatbot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: linear-gradient(135deg, var(--brand-navy-900), var(--brand-navy-700));
  color: var(--text-inverse);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  .chatbot-title {
    display: flex;
    align-items: center;
    gap: var(--space-3);

    div {
      min-width: 0;
    }

    .icon {
      width: 38px;
      height: 38px;
      border-radius: var(--radius-lg);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-inverse);
      font-size: var(--text-sm);
      font-weight: var(--weight-semibold);
      letter-spacing: var(--tracking-wider);
      border: 1px solid rgba(255, 255, 255, 0.14);
      flex-shrink: 0;

      :deep(svg) {
        width: 22px;
        height: 22px;
      }
    }

    h3 {
      margin: 0;
      font-size: var(--text-lg);
      font-weight: var(--weight-semibold);
      line-height: var(--leading-tight);
      color: var(--text-inverse);
    }

    p {
      margin: 2px 0 0;
      font-size: var(--text-sm);
      color: rgba(255, 255, 255, 0.72);
    }
  }

  .header-actions {
    display: flex;
    gap: var(--space-2);
    align-items: center;

    .btn-icon,
    .btn-close {
      background: rgba(255, 255, 255, 0.12);
      border: none;
      color: var(--text-inverse);
      cursor: pointer;
      border-radius: var(--radius-md);
      width: 36px;
      height: 36px;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: var(--text-base);
      transition:
        background var(--duration-fast) var(--ease-out),
        transform var(--duration-fast) var(--ease-out);

      &:hover {
        background: rgba(255, 255, 255, 0.18);
        transform: translateY(-1px);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

.suggestions-panel {
  background: $surface-base;
  border: 1px solid $border-color;
  border-radius: 10px;
  padding: 12px;

  .suggestions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    .btn-link {
      background: transparent;
      border: none;
      color: $primary-color;
      cursor: pointer;
      font-size: 13px;
    }
  }

  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .suggestion-item {
    width: 100%;
    text-align: left;
    background: $surface-subtle;
    border: 1px solid $border-color;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: $text-color;
    transition: all 0.2s;

    &:hover {
      background: var(--status-info-bg);
      border-color: $primary-color;
      color: var(--status-info-text);
    }
  }
}

// Messages Container
.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: $surface-subtle;
}

// Empty State
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;

  .greeting {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 8px;
    color: $text-color;
    display: inline-flex;
    align-items: center;
    gap: 8px;

    .greeting-icon {
      width: 20px;
      height: 20px;
      color: $primary-color;
      flex-shrink: 0;
    }
  }

  .subtitle {
    font-size: 14px;
    color: $text-light;
    margin: 0 0 16px;
  }

  .quick-prompts {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;

    .prompt-btn {
      background: $surface-base;
      border: 1px solid $border-color;
      padding: 10px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      color: $text-color;
      transition: all 0.2s;

      &:hover {
        background: $primary-color;
        color: white;
        border-color: $primary-color;
      }
    }
  }
}

// Messages
.message {
  display: flex;
  gap: 8px;
  animation: slideIn 0.3s ease;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  &.message-user {
    justify-content: flex-end;

    .message-content {
      background: $primary-color;
      color: white;
      margin-left: auto;
    }
  }

  &.message-bot {
    justify-content: flex-start;

    .message-avatar {
      min-width: 32px;
      color: $primary-color;

      :deep(svg) {
        width: 24px;
        height: 24px;
      }
    }

    .message-body {
      flex: 1;
    }

    .message-content {
      background: $surface-base;
      color: $text-color;
      border: 1px solid $border-color;
    }
  }

  &.message-error {
    justify-content: flex-start;
    align-items: center;
    gap: 12px;

    .error-icon {
      color: $danger-color;

      :deep(svg) {
        width: 20px;
        height: 20px;
      }
    }

    .error-content {
      background: var(--status-danger-bg);
      color: var(--status-danger-text);
      padding: 10px 12px;
      border-radius: 6px;
      border-left: 3px solid var(--status-danger-border);
    }
  }

  &.message-loading {
    .typing-indicator {
      display: flex;
      gap: 4px;

      span {
        width: 8px;
        height: 8px;
        background: $text-light;
        border-radius: 50%;
        animation: bounce 1.4s infinite;

        &:nth-child(2) {
          animation-delay: 0.2s;
        }

        &:nth-child(3) {
          animation-delay: 0.4s;
        }
      }
    }

    @keyframes bounce {
      0%,
      80%,
      100% {
        opacity: 0.5;
      }
      40% {
        opacity: 1;
      }
    }
  }
}

// Message Content
.message-content {
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;

  &.user-content {
    max-width: 100%;
  }

  &.bot-content {
    max-width: 100%;

    div {
      margin: 4px 0;

      &:first-child {
        margin-top: 0;
      }

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

// Message Meta
.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 12px;
}

.message-time {
  color: $text-light;
  font-size: 12px;
}

.intent-badge {
  background: var(--status-info-bg);
  color: var(--status-info-text);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

// Input Area
.chatbot-input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid $border-color;
  background: $surface-base;

  .message-input {
    flex: 1;
    border: 1px solid $border-color;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
    font-family: inherit;
    resize: none;
    max-height: 100px;
    transition: border-color 0.2s;
    background: $surface-base;
    color: $text-color;

    &:focus {
      outline: none;
      border-color: $primary-color;
      box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
    }

    &:disabled {
      background: $surface-subtle;
      cursor: not-allowed;
    }
  }

  .btn-send {
    background: $primary-color;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 14px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 44px;

    :deep(svg) {
      width: 18px;
      height: 18px;
    }

    &:hover:not(:disabled) {
      background: $primary-dark;
    }

    &:disabled {
      background: #ccc;
      cursor: not-allowed;
    }

    .spinner {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  }
}

// Footer
.chatbot-footer {
  padding: 8px 12px;
  background: $surface-subtle;
  text-align: center;
  font-size: 12px;
  color: $text-light;
  border-top: 1px solid $border-color;
}

// Toggle Button
.chatbot-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: $primary-color;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  z-index: 998;

  &:hover {
    background: $primary-dark;
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  &:active {
    transform: scale(0.95);
  }

  .toggle-icon {
    display: flex;
    align-items: center;
    justify-content: center;

    :deep(svg) {
      width: 26px;
      height: 26px;
    }
  }

  .message-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    background: $danger-color;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    border: 2px solid white;
  }
}

// Scrollbar
.chatbot-messages {
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;

    &:hover {
      background: #999;
    }
  }
}
</style>
