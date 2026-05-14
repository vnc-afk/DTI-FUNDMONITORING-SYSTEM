/**
 * ChatBot Chat Page
 * Full-page chat interface for the chatbot
 */

<template>
  <div class="chatbot-page">
    <div class="page-header">
      <h1 class="page-title">
        <MessageCircle class="title-icon" aria-hidden="true" />
        <span>Fund Monitor Assistant</span>
      </h1>
      <p class="subtitle">Ask me anything about your funds, expenses, suppliers, and reports</p>
    </div>

    <div class="chat-container">
      <!-- Messages -->
      <div class="messages-area" data-testid="chat-messages">
        <div v-if="!hasMessages" class="welcome-message">
          <div class="welcome-icon">
            <Bot aria-hidden="true" />
          </div>
          <h2>Welcome to Fund Monitor Assistant!</h2>
          <p>I can help you with:</p>
          <ul class="features-list">
            <li v-for="feature in features" :key="feature.label" class="feature-item">
              <component :is="feature.icon" class="feature-icon" aria-hidden="true" />
              <span>{{ feature.label }}</span>
            </li>
          </ul>
          <p class="start-hint">Type your question below to get started!</p>
        </div>

        <div v-else>
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-group"
            :class="`message-${message.type}`"
          >
            <!-- User Message -->
            <div v-if="message.type === 'user'" class="message-item user-message">
              <div class="message-bubble">{{ message.content }}</div>
              <span class="message-timestamp">{{ formatTime(message.timestamp) }}</span>
            </div>

            <!-- Bot Message -->
            <div v-else-if="message.type === 'bot'" class="message-item bot-message">
              <div class="bot-avatar">
                <Bot aria-hidden="true" />
              </div>
              <div class="message-main">
                <div class="message-bubble">
                  <div v-for="(line, idx) in formatMessageContent(message.content)" :key="idx">
                    {{ line }}
                  </div>
                </div>
                <div class="message-info">
                  <span class="message-timestamp">{{ formatTime(message.timestamp) }}</span>
                  <span
                    v-if="message.intent !== 'unknown'"
                    class="intent-tag"
                    :title="`Confidence: ${(message.confidence * 100).toFixed(0)}%`"
                  >
                    {{ message.intent }} • {{ (message.confidence * 100).toFixed(0) }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- Error Message -->
            <div v-else-if="message.type === 'error'" class="message-item error-message">
              <div class="error-icon">
                <AlertTriangle aria-hidden="true" />
              </div>
              <div class="error-bubble">{{ message.content }}</div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="message-item bot-message">
          <div class="bot-avatar">
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
      <div class="input-area">
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

        <div class="input-group">
          <textarea
            v-model="inputMessage"
            class="message-input"
            placeholder="Ask about funds, expenses, suppliers, reports..."
            @keydown="handleKeydown"
            :disabled="isLoading"
            rows="3"
          ></textarea>
          <button
            class="send-button"
            @click="handleSendMessage"
            :disabled="isLoading || !inputMessage.trim()"
          >
            <span v-if="!isLoading">Send</span>
            <span v-else>Sending...</span>
          </button>
        </div>

        <div v-if="hasMessages" class="action-buttons">
          <button class="btn-secondary" @click="handleClear">Clear Chat</button>
          <button
            class="btn-secondary"
            :class="{ active: showSuggestions }"
            @click="toggleSuggestions"
          >
            Suggestions
          </button>
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
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { AlertTriangle, Bot, Building2, Coins, Landmark, MessageCircle, PieChart, RefreshCw, TrendingUp } from 'lucide-vue-next'
import { useChatbot } from '@/composables/useChatbot'

const {
  inputMessage,
  messages,
  isLoading,
  hasMessages,
  showClearModal,
  handleSendMessage,
  handleClear,
  confirmClearMessages,
  cancelClearMessages,
  handleKeydown,
  formatTime,
  formatMessageContent,
} = useChatbot()

// Suggestions list and UI state
const showSuggestions = ref(false)
const suggestionsPanel = ref(null)
const features = [
  { icon: Coins, label: 'Check total available funds' },
  { icon: PieChart, label: 'View fund allocation breakdown' },
  { icon: TrendingUp, label: 'Track daily, weekly, or monthly expenses' },
  { icon: Building2, label: 'Look up supplier information' },
  { icon: RefreshCw, label: 'Monitor bank reconciliation status' },
  { icon: Landmark, label: 'Get financial summaries and reports' },
]
const suggestions = [
  "What's my total available funds?",
  "Show fund allocation by source",
  "How much was spent today?",
  "Expenses this week",
  "Give me this month's summary",
  "Top 5 highest expenses",
  "List all suppliers",
  "Who is the top supplier?",
  "Show unreconciled transactions",
  "Bank reconciliation status",
  "Overall financial summary",
  "Show user activity stats",
]

function toggleSuggestions() {
  showSuggestions.value = !showSuggestions.value

  if (showSuggestions.value) {
    nextTick(() => {
      suggestionsPanel.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

async function selectSuggestion(q) {
  // populate input and send
  inputMessage.value = q
  showSuggestions.value = false
  await handleSendMessage()
}
</script>

<style scoped lang="scss">
$primary-color: var(--brand-navy-700);
$primary-dark: var(--brand-navy-600);
$light-gray: var(--surface-page);
$border-color: var(--border-default);
$text-color: var(--text-primary);
$text-light: var(--text-tertiary);
$danger-color: var(--status-danger-text);
$surface-base: var(--surface-base);
$surface-subtle: var(--surface-subtle);

.chatbot-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $light-gray;

  .page-header {
    padding: 24px;
    background: $surface-base;
    border-bottom: 1px solid $border-color;
    text-align: center;

    h1 {
      margin: 0 0 8px;
      font-size: 28px;
      color: $text-color;
    }

    .page-title {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;

      .title-icon {
        width: 28px;
        height: 28px;
        color: $primary-color;
      }
    }

    .subtitle {
      margin: 0;
      color: $text-light;
      font-size: 14px;
    }
  }

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .messages-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .welcome-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 40px 20px;

    .welcome-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 72px;
      height: 72px;
      margin-bottom: 16px;
      color: $primary-color;

      svg {
        width: 64px;
        height: 64px;
      }
    }

    h2 {
      margin: 0 0 16px;
      font-size: 24px;
      color: $text-color;
    }

    p {
      margin: 0 0 12px;
      color: $text-light;

      &.start-hint {
        margin-top: 24px;
        font-size: 14px;
        font-weight: 500;
      }
    }

    .features-list {
      list-style: none;
      padding: 0;
      margin: 12px 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      text-align: left;

      .feature-item {
        display: flex;
        align-items: center;
        gap: 10px;
        background: $surface-base;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid $border-color;
        font-size: 14px;
        transition: all 0.2s;

        .feature-icon {
          width: 16px;
          height: 16px;
          color: $primary-color;
          flex-shrink: 0;
        }

        &:hover {
          border-color: $primary-color;
          box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
        }
      }
    }
  }

  .message-group {
    display: flex;
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
    }

    &.message-bot {
      justify-content: flex-start;
    }

    &.message-error {
      justify-content: flex-start;
    }
  }

  .message-item {
    display: flex;
    gap: 12px;
    max-width: 80%;

    &.user-message {
      justify-content: flex-end;
      align-self: flex-end;
      flex-direction: column;
      align-items: flex-end;

      .message-bubble {
        background: $primary-color;
        color: white;
        padding: 12px 16px;
        border-radius: 12px;
        border-bottom-right-radius: 4px;
        word-wrap: break-word;
      }

      .message-timestamp {
        font-size: 12px;
        color: $text-light;
        margin-top: 6px;
        margin-right: 4px;
      }
    }

    &.bot-message {
      align-self: flex-start;

      .bot-avatar {
        min-width: 40px;
        text-align: center;
        color: $primary-color;

        svg {
          width: 28px;
          height: 28px;
        }
      }

      .message-main {
        flex: 1;
      }

      .message-bubble {
        background: $surface-base;
        color: $text-color;
        padding: 12px 16px;
        border-radius: 12px;
        border-bottom-left-radius: 4px;
        border: 1px solid $border-color;
        word-wrap: break-word;

        div {
          margin: 6px 0;

          &:first-child {
            margin-top: 0;
          }

          &:last-child {
            margin-bottom: 0;
          }
        }
      }

      .message-info {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-top: 8px;
        margin-left: 4px;
      }

      .message-timestamp {
        font-size: 12px;
        color: $text-light;
      }

      .intent-tag {
        background: var(--status-info-bg);
        color: var(--status-info-text);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
      }
    }

    &.error-message {
      .error-icon {
        min-width: 40px;
        color: var(--status-danger-text);

        svg {
          width: 20px;
          height: 20px;
        }
      }

      .error-bubble {
        background: var(--status-danger-bg);
        color: var(--status-danger-text);
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 3px solid var(--status-danger-border);
      }
    }
  }

  .typing-indicator {
    display: flex;
    gap: 6px;
    padding: 12px 16px;

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

  .input-area {
    padding: 20px;
      background: $surface-base;
    .input-group {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;

      .message-input {
        flex: 1;
        border: 1px solid $border-color;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        font-family: inherit;
        resize: vertical;
        min-height: 80px;
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

      .send-button {
        background: $primary-color;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        cursor: pointer;
        font-weight: 600;
        transition: background 0.2s;
        min-width: 100px;

        &:hover:not(:disabled) {
          background: $primary-dark;
        }

        &:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      }
    }

    .action-buttons {
      display: flex;
      gap: 12px;

      .btn-secondary {
        flex: 1;
        background: $light-gray;
        border: 1px solid $border-color;
        padding: 10px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;

        &:hover {
          background: white;
          border-color: $primary-color;
          color: $primary-color;
        }
      }
    }

    .suggestions-panel {
      background: #fbfbff;
      border: 1px solid $border-color;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 12px;

      .suggestions-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

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
        flex-wrap: wrap;
        gap: 8px;
      }

      .suggestion-item {
        background: white;
        border: 1px solid $border-color;
        padding: 8px 10px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;

        &:hover {
          border-color: $primary-color;
          color: $primary-color;
        }
      }
    }

    .btn-secondary.active {
      background: #e8f4fd;
      border-color: $primary-color;
      color: $primary-color;
    }
  }
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: color-mix(in srgb, var(--surface-page) 72%, transparent);
  backdrop-filter: blur(10px);
}

.clear-modal {
  width: min(100%, 380px);
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid $border-color;
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
  gap: 12px;
  padding: 24px 24px 12px;
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
  color: $text-color;
  font-size: 18px;
}

.clear-modal-body {
  margin: 0;
  padding: 0 24px;
  color: $text-light;
  font-size: 14px;
  line-height: 1.5;
}

.clear-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding: 0 24px 24px;
}

// Scrollbar
.messages-area {
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;

    &:hover {
      background: #999;
    }
  }
}

@media (max-width: 768px) {
  .chatbot-page {
    .message-item {
      max-width: 95%;
    }

    .page-header {
      padding: 16px;

      h1 {
        font-size: 20px;
      }

      .subtitle {
        font-size: 12px;
      }
    }

    .input-area {
      padding: 12px;

      .input-group {
        flex-direction: column;

        .send-button {
          width: 100%;
        }
      }
    }
  }
}
</style>
