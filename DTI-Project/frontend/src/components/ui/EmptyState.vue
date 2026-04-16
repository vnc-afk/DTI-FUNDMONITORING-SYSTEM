<template>
  <div class="empty-state" role="status" aria-live="polite">
    <ui-icon :name="icon" :size="iconSize" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <div v-if="$slots.actions" class="empty-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import UiIcon from './UiIcon.vue'

defineProps({
  icon: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
  iconSize: { type: Number, default: 48 },
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-8);
  min-height: 300px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-state h3 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
  font-weight: 600;
}

.empty-state p {
  margin: 0;
  max-width: 400px;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.empty-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
  flex-wrap: wrap;
  justify-content: center;
}

:deep(.empty-state svg) {
  color: var(--text-tertiary);
}
</style>
