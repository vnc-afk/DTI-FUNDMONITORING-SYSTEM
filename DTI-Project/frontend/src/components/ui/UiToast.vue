<template>
  <teleport to="body">
    <div v-if="isVisible" class="toast" :class="`toast-${resolvedVariant}`">
      <div class="toast-content">
        <div class="toast-icon" v-if="icon">
          <component :is="icon" :size="20" />
        </div>
        <div class="toast-message">
          <h4 v-if="title" class="toast-title">{{ title }}</h4>
          <p v-if="message" class="toast-text">{{ message }}</p>
        </div>
        <button v-if="dismissible" type="button" class="toast-close" @click="close" aria-label="Close notification">
          <ui-icon name="x" size="16" />
        </button>
      </div>
      <div class="toast-progress" v-if="autoClose" :style="{ animationDuration: `${duration}ms` }" />
    </div>
  </teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import UiIcon from './UiIcon.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: undefined },
  message: { type: String, default: '' },
  title: { type: String, default: '' },
  variant: { type: String, default: 'info', validator: (v) => ['success', 'error', 'warning', 'info', 'danger'].includes(v) },
  duration: { type: Number, default: 5000 },
  autoClose: { type: Boolean, default: true },
  dismissible: { type: Boolean, default: true },
  icon: { type: [Object, String], default: null },
})

const emit = defineEmits(['close', 'update:modelValue'])
const visible = ref(props.modelValue ?? true)
const resolvedVariant = computed(() => (props.variant === 'danger' ? 'error' : props.variant))
const hasContent = computed(() => Boolean(props.title || props.message))
const isVisible = computed(() => visible.value && hasContent.value)

let autoCloseTimer = null

function clearAutoCloseTimer() {
  if (autoCloseTimer !== null) {
    window.clearTimeout(autoCloseTimer)
    autoCloseTimer = null
  }
}

function scheduleAutoClose() {
  clearAutoCloseTimer()

  if (!props.autoClose || !visible.value || !hasContent.value) {
    return
  }

  autoCloseTimer = window.setTimeout(() => {
    close()
  }, props.duration)
}

const close = () => {
  clearAutoCloseTimer()
  visible.value = false
  emit('update:modelValue', false)
  emit('close')
}

watch(
  () => props.modelValue,
  (value) => {
    if (value === undefined) {
      return
    }

    visible.value = Boolean(value)
    scheduleAutoClose()
  },
  { immediate: true }
)

watch(visible, (value) => {
  if (props.modelValue !== undefined) {
    emit('update:modelValue', value)
  }

  if (!value) {
    clearAutoCloseTimer()
  }
})

if (props.modelValue === undefined) {
  scheduleAutoClose()
}

onBeforeUnmount(() => {
  clearAutoCloseTimer()
})
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  min-width: 300px;
  max-width: 500px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-toast);
  animation: slideIn var(--duration-fast) var(--ease-out);
  overflow: hidden;
}

.toast-success {
  background: var(--status-success-bg);
  border: 1px solid var(--status-success-border);
  color: var(--status-success-text);
}

.toast-error {
  background: var(--status-danger-bg);
  border: 1px solid var(--status-danger-border);
  color: var(--status-danger-text);
}

.toast-warning {
  background: var(--status-warning-bg);
  border: 1px solid var(--status-warning-border);
  color: var(--status-warning-text);
}

.toast-info {
  background: var(--status-info-bg);
  border: 1px solid var(--status-info-border);
  color: var(--status-info-text);
}

.toast-content {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
}

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  margin-top: 2px;
}

.toast-message {
  flex: 1;
}

.toast-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  margin: 0 0 var(--space-1) 0;
}

.toast-text {
  font-size: var(--text-sm);
  margin: 0;
  line-height: var(--leading-relaxed);
}

.toast-close {
  flex-shrink: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  opacity: 0.6;
  transition: opacity var(--duration-fast) var(--ease-out);
}

.toast-close:hover {
  opacity: 1;
}

.toast-progress {
  height: 2px;
  background: currentColor;
  opacity: 0.3;
  animation: progress linear forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0;
  }
}

@media (max-width: 640px) {
  .toast {
    left: var(--space-4);
    right: var(--space-4);
    bottom: var(--space-4);
    min-width: 0;
    max-width: none;
    width: auto;
  }

  .toast-content {
    padding: var(--space-3);
  }

  .toast-title,
  .toast-text {
    font-size: var(--text-sm);
  }
}

</style>