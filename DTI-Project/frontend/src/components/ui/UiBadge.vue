<template>
  <span 
    class="ui-badge" 
    :class="[
      `ui-badge--${resolvedVariant}`,
      `ui-badge--${size}`,
      { 'ui-badge--pill': pill }
    ]"
    :role="dismissible ? 'status' : undefined"
  >
    <slot>{{ text }}</slot>
    
    <button
      v-if="dismissible"
      type="button"
      class="ui-badge__close"
      :aria-label="`Close ${text || 'badge'}`"
      @click="$emit('dismiss')"
    >
      <ui-icon name="x" size="14" />
    </button>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import UiIcon from './UiIcon.vue'

const props = defineProps({
  text: { type: String, default: '' },
  variant: {
    type: String,
    default: 'neutral',
    validator: (value) => ['neutral', 'success', 'warning', 'danger', 'info', 'error', 'default'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md'].includes(value),
  },
  pill: { type: Boolean, default: false },
  dismissible: { type: Boolean, default: false },
})

defineEmits(['dismiss'])

const resolvedVariant = computed(() => {
  if (props.variant === 'error') return 'danger'
  if (props.variant === 'default') return 'neutral'
  return props.variant
})
</script>

<style scoped>
/* ── Badge Base ────────────────────────────────────────────────────────────── */
.ui-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  border: none;
  border-radius: var(--radius-md);
  white-space: nowrap;
  transition: all var(--duration-fast) var(--ease-out);
  user-select: none;
}

/* ── Sizes ──────────────────────────────────────────────────────────────────── */
.ui-badge--sm {
  font-size: var(--text-xs);
  padding: 0.25rem 0.625rem;
  min-height: 20px;
  line-height: 1.2;
}

.ui-badge--md {
  font-size: var(--text-sm);
  padding: 0.375rem 0.75rem;
  min-height: 24px;
  line-height: 1.25;
}

/* ── Pill Style ────────────────────────────────────────────────────────────── */
.ui-badge--pill {
  border-radius: 9999px;
}

/* ── Variants ──────────────────────────────────────────────────────────────── */
/* Neutral */
.ui-badge--neutral {
  background-color: var(--surface-subtle);
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.ui-badge--neutral:hover {
  background-color: var(--surface-base);
  border-color: var(--border-base);
}

/* Success */
.ui-badge--success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--status-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.ui-badge--success:hover {
  background-color: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

/* Warning */
.ui-badge--warning {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--status-warning, #f59e0b);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.ui-badge--warning:hover {
  background-color: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

/* Danger */
.ui-badge--danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--status-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.ui-badge--danger:hover {
  background-color: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Info */
.ui-badge--info {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--brand-navy-600);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.ui-badge--info:hover {
  background-color: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
}

/* ── Close Button ──────────────────────────────────────────────────────────── */
.ui-badge__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity var(--duration-fast) var(--ease-out);
  line-height: 1;
  font-size: inherit;
  color: inherit;
}

.ui-badge__close:hover {
  opacity: 1;
}

.ui-badge__close:focus-visible {
  outline: 2px solid transparent;
  outline-offset: 2px;
  opacity: 1;
}
</style>
