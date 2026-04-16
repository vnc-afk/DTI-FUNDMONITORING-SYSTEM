<template>
  <div class="no-results">
    <div class="no-results-icon">
      <ui-icon name="inbox" size="48" />
    </div>
    <h3 class="no-results-title">{{ title || 'No Results' }}</h3>
    <p class="no-results-desc" v-if="description">{{ description }}</p>
    <div class="no-results-actions" v-if="$slots.default">
      <slot />
    </div>
  </div>
</template>

<script setup>
import UiIcon from '@/components/ui/UiIcon.vue'

defineProps({
  title: { type: String, default: 'No Results' },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
  color: var(--text-tertiary);
}

.no-results-icon {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
  color: var(--text-muted);
}

.no-results-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.no-results-desc {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0 0 var(--space-4) 0;
  max-width: 400px;
}

.no-results-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}
</style>
