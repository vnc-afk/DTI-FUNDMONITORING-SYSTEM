<template>
  <div class="form-section">
    <h3 v-if="hasTitle" class="form-section-title">
      <slot name="title">{{ title }}</slot>
    </h3>
    <slot />
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
})

const slots = useSlots()

const hasTitle = computed(() => Boolean(props.title || slots.title))
</script>

<style scoped>
.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6);
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-6);
}

.form-section-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

@media (max-width: 768px) {
  .form-section {
    padding: var(--space-4);
  }
}
</style>
