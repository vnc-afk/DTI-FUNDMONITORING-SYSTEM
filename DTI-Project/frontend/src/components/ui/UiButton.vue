<template>
  <component
    :is="resolvedTag"
    class="ui-button"
    :class="[
      `ui-button--${variant}`,
      `ui-button--${size}`,
      { 'ui-button--block': block, 'is-loading': loading }
    ]"
    :type="buttonType"
    :to="resolvedTo"
    :disabled="isDisabled"
    :href="resolvedHref"
    @click="onClick"
  >
    <span class="ui-button__content">
      <slot />
    </span>
    <span v-if="loading" class="ui-button__spinner"></span>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  tag: { type: String, default: 'button' },
  type: { type: String, default: 'button' },
  to: { type: [String, Object], default: '' },
  href: { type: String, default: '' },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'ghost', 'warning', 'danger'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  block: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const isRouterLink = computed(() => Boolean(props.to))
const isDisabled = computed(() => props.disabled || props.loading)
const resolvedTag = computed(() => (isRouterLink.value ? RouterLink : props.tag))
const resolvedTo = computed(() => (isRouterLink.value ? props.to : undefined))
const resolvedHref = computed(() => (isRouterLink.value ? undefined : props.href))
const buttonType = computed(() => (props.tag === 'button' && !isRouterLink.value ? props.type : undefined))

function onClick(event) {
  if (isDisabled.value) {
    event.preventDefault()
    return
  }
  emit('click', event)
}
</script>

<style scoped>
/* ── Button Base ────────────────────────────────────────────────────────────── */
.ui-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  text-decoration: none;
  user-select: none;
  padding: var(--space-2) var(--space-3);
  min-width: 0;
  max-width: 100%;
}

.ui-button:focus-visible {
  outline: 2px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 0 0 3px rgba(46, 80, 128, 0.1), 0 0 0 2px var(--brand-navy-600);
}

/* ── Sizes ──────────────────────────────────────────────────────────────────── */
.ui-button--sm {
  font-size: var(--text-sm);
  padding: var(--space-1) var(--space-2);
  min-height: 32px;
}

.ui-button--md {
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-4);
  min-height: 40px;
}

.ui-button--lg {
  font-size: var(--text-base);
  padding: var(--space-3) var(--space-6);
  min-height: 48px;
}

/* ── Primary Variant ───────────────────────────────────────────────────────── */
.ui-button--primary {
  background: linear-gradient(135deg, var(--brand-navy-600), var(--brand-navy-700));
  color: white;
  box-shadow: 0 2px 4px rgba(46, 80, 128, 0.2);
}

.ui-button--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--brand-navy-700), var(--brand-navy-800));
  box-shadow: 0 4px 12px rgba(46, 80, 128, 0.3);
  transform: translateY(-1px);
}

.ui-button--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(46, 80, 128, 0.2);
}

/* ── Secondary Variant ────────────────────────────────────────────────────── */
.ui-button--secondary {
  background: var(--surface-subtle);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.ui-button--secondary:hover:not(:disabled) {
  background: var(--surface-base);
  border-color: var(--border-strong);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.ui-button--secondary:active:not(:disabled) {
  background: var(--surface-subtle);
  transform: translateY(0);
}

/* ── Ghost Variant ────────────────────────────────────────────────────────── */
.ui-button--ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.ui-button--ghost:hover:not(:disabled) {
  background: var(--surface-subtle);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}

.ui-button--ghost:active:not(:disabled) {
  background: color-mix(in srgb, var(--surface-subtle) 80%, transparent);
}

/* ── Warning Variant ──────────────────────────────────────────────────────── */
.ui-button--warning {
  background: var(--status-warning-bg);
  color: var(--status-warning-text);
  border: 1px solid var(--status-warning-border);
}

.ui-button--warning:hover:not(:disabled) {
  background: color-mix(in srgb, var(--status-warning-bg) 85%, white);
  border-color: var(--status-warning-text);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.ui-button--warning:active:not(:disabled) {
  background: var(--status-warning-bg);
  transform: translateY(0);
}

/* ── Danger Variant ────────────────────────────────────────────────────────── */
.ui-button--danger {
  background: linear-gradient(135deg, var(--status-danger), var(--status-danger-dark, #d32f2f));
  color: white;
  box-shadow: 0 2px 4px rgba(211, 47, 47, 0.2);
}

.ui-button--danger:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--status-danger-dark, #d32f2f), var(--status-danger-darker, #b71c1c));
  box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
  transform: translateY(-1px);
}

.ui-button--danger:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(211, 47, 47, 0.2);
}

/* ── Block ──────────────────────────────────────────────────────────────────── */
.ui-button--block {
  width: 100%;
}

/* ── Disabled State ────────────────────────────────────────────────────────── */
.ui-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Loading State ────────────────────────────────────────────────────────── */
.ui-button.is-loading {
  pointer-events: none;
}

.ui-button.is-loading .ui-button__content {
  opacity: 0.7;
}

.ui-button__spinner {
  position: absolute;
  display: none;
}

.ui-button.is-loading .ui-button__spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: ui-button-spin 0.8s linear infinite;
}

@keyframes ui-button-spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── Icon Styling ──────────────────────────────────────────────────────────── */
.ui-button i {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1em;
  transition: transform var(--duration-normal) var(--ease-out);
}

.ui-button:hover:not(:disabled) i {
  transform: scale(1.1);
}

/* ── Content ───────────────────────────────────────────────────────────────── */
.ui-button__content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all var(--duration-fast) var(--ease-out);
}

@media (max-width: 640px) {
  .ui-button--sm {
    min-height: 40px;
  }

  .ui-button--md {
    min-height: 44px;
  }

  .ui-button--lg {
    min-height: 48px;
  }
}
</style>

