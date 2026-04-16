<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay">
        <div class="modal-container" @click.self="close">
          <div class="modal-dialog">
            <div class="modal-header">
              <h3 class="modal-title">{{ title }}</h3>
              <button
                type="button"
                class="modal-close-btn"
                @click="close"
                aria-label="Close dialog"
              >
                <ui-icon name="x" size="20" />
              </button>
            </div>

            <div class="modal-body">
              <p class="modal-message">{{ message }}</p>
              <div v-if="details" class="modal-details">
                <code>{{ details }}</code>
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-modal-secondary"
                @click="close"
              >
                {{ cancelLabel }}
              </button>
              <button
                type="button"
                class="btn btn-modal-danger"
                :disabled="isLoading"
                @click="confirm"
              >
                <ui-icon v-if="isLoading" name="loader" size="16" class="spinner-icon" />
                {{ isLoading ? loadingLabel : confirmLabel }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import UiIcon from '@/components/ui/UiIcon.vue'

defineProps({
  title: { type: String, default: 'Confirm Delete' },
  message: { type: String, required: true },
  details: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Delete' },
  loadingLabel: { type: String, default: 'Deleting...' },
  cancelLabel: { type: String, default: 'Cancel' },
  isLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'close'])

const isOpen = ref(false)

function open() {
  isOpen.value = true
  document.body.style.overflow = 'hidden'
}

function close() {
  isOpen.value = false
  document.body.style.overflow = ''
  emit('close')
}

function confirm() {
  emit('confirm')
}

defineExpose({ open, close })
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

.modal-container {
  width: 100%;
  max-width: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Modal Dialog */
.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Modal Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-soft);
  background: var(--bg-elevated);
}

.modal-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-base);
  flex-shrink: 0;
}

.modal-close-btn:hover:not(:disabled) {
  background: var(--bg-card);
  color: var(--text-secondary);
}

.modal-close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Body */
.modal-body {
  padding: var(--space-4);
}

.modal-message {
  margin: 0 0 var(--space-3) 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  line-height: 1.6;
}

.modal-details {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-elevated);
  border-left: 3px solid var(--status-danger);
  border-radius: var(--radius-sm);
  overflow-x: auto;
}

.modal-details code {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-family: 'Courier New', 'Monaco', monospace;
  word-break: break-all;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-4);
  border-top: 1px solid var(--border-soft);
  background: var(--bg-elevated);
}

/* Modal Buttons */
.btn {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: var(--text-sm);
  border: 1px solid;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  min-height: 40px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-modal-secondary {
  background: var(--bg-card);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.btn-modal-secondary:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.btn-modal-danger {
  background: var(--status-danger);
  border-color: var(--status-danger);
  color: white;
}

.btn-modal-danger:hover:not(:disabled) {
  background: color-mix(in srgb, var(--status-danger) 85%, black);
  border-color: color-mix(in srgb, var(--status-danger) 85%, black);
}

.spinner-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 480px) {
  .modal-overlay {
    padding: var(--space-3);
  }

  .modal-dialog {
    width: 100%;
  }

  .modal-header {
    padding: var(--space-3);
  }

  .modal-body {
    padding: var(--space-3);
  }

  .modal-footer {
    padding: var(--space-3);
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>

