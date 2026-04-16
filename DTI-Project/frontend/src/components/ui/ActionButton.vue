<template>
  <component
    :is="tag"
    class="action-btn"
    :class="`action-btn-${variant}`"
    :type="tag === 'button' ? 'button' : undefined"
    :to="to"
    :title="title"
    @click="$emit('click')"
  >
    <slot />
  </component>
</template>

<script setup>
defineProps({
  tag: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'router-link', 'a'].includes(value),
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'danger', 'secondary', 'success'].includes(value),
  },
  to: { type: String, default: '' },
  title: { type: String, default: '' },
})

defineEmits(['click'])
</script>

<style scoped>
.action-btn {
  position: relative;
  background: transparent;
  border: 1.5px solid transparent;
  color: var(--text-tertiary);
  padding: var(--space-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
  min-width: 40px;
  min-height: 40px;
  text-decoration: none;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn-primary {
  color: var(--brand-navy-600);
}

.action-btn-primary:hover {
  background: color-mix(in srgb, var(--brand-navy-600) 12%, transparent);
  border-color: var(--brand-navy-600);
  box-shadow: var(--shadow-md);
}

.action-btn-primary:active {
  transform: translateY(0);
}

.action-btn-danger {
  color: var(--status-danger-text);
}

.action-btn-danger:hover {
  background: var(--status-danger-bg);
  border-color: var(--status-danger-border);
  box-shadow: var(--shadow-md);
}

.action-btn-danger:active {
  transform: translateY(0);
}

.action-btn-secondary {
  color: var(--text-tertiary);
}

.action-btn-secondary:hover {
  background: var(--bg-elevated);
  border-color: var(--border-soft);
  box-shadow: var(--shadow-md);
  color: var(--text-primary);
}

.action-btn-secondary:active {
  transform: translateY(0);
}

.action-btn-success {
  color: var(--status-success-text);
}

.action-btn-success:hover {
  background: color-mix(in srgb, var(--status-success) 15%, transparent);
  border-color: var(--status-success);
  box-shadow: var(--shadow-md);
}

.action-btn-success:active {
  transform: translateY(0);
}
</style>
