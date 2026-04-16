<template>
  <teleport to="body">
    <div v-if="modelValue" class="drawer-overlay" @click="handleClose">
      <div class="drawer" :class="[`drawer-${position}`]" @click.stop>
        <div class="drawer-header">
          <h2 v-if="title" class="drawer-title">{{ title }}</h2>
          <button type="button" class="drawer-close" @click="handleClose" aria-label="Close drawer">
            <ui-icon name="x" size="20" />
          </button>
        </div>
        <div class="drawer-body">
          <slot />
        </div>
        <div class="drawer-footer" v-if="$slots.footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import UiIcon from './UiIcon.vue'

defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  position: { type: String, default: 'right', validator: (v) => ['left', 'right'].includes(v) },
})

const emit = defineEmits(['update:modelValue'])

const handleClose = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: var(--z-modal);
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 400px;
  background: var(--surface-base);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  z-index: calc(var(--z-modal) + 1);
  animation: slideIn var(--duration-fast) var(--ease-out);
}

.drawer-right {
  right: 0;
}

.drawer-left {
  left: 0;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.drawer-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.drawer-close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--duration-fast) var(--ease-out);
  padding: var(--space-1);
}

.drawer-close:hover {
  color: var(--text-primary);
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.drawer-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-subtle);
  background: var(--surface-subtle);
  flex-shrink: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.drawer-left {
  animation: slideInLeft var(--duration-fast) var(--ease-out);
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@media (max-width: 640px) {
  .drawer {
    width: 100%;
  }
}
</style>
