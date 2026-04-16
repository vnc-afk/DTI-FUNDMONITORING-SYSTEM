<template>
  <div class="dashboard-page">
    <!-- Custom Header Slot (if provided) -->
    <slot name="header" />

    <!-- Fallback Default Header -->
    <div v-if="!$slots.header && showDefaultHeader" class="page-header">
      <div class="page-header-info">
        <div class="page-header-eyebrow" v-if="eyebrow">{{ eyebrow }}</div>
        <h1 class="page-header-title">{{ title }}</h1>
        <p class="page-header-desc" v-if="description">{{ description }}</p>
      </div>
      <div class="page-header-actions">
        <slot name="header-actions" />
      </div>
    </div>

    <!-- Filters Slot -->
    <slot name="filters" />

    <!-- Summary cards slot -->
    <slot name="summary" />

    <!-- Main Content (Charts, etc.) -->
    <slot name="content" />

    <!-- Fallback Content Grid (for backward compatibility) -->
    <div v-if="!$slots.content" class="dashboard-grid">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
})

const showDefaultHeader = computed(() => Boolean(props.title || props.description || props.eyebrow))
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  min-width: 0;
}

.page-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.page-header-info {
  flex: 1;
  min-width: 0;
}

.page-header-eyebrow {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-widest);
  color: var(--text-tertiary);
  margin-bottom: var(--space-1);
}

.page-header-title {
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
  line-height: var(--leading-tight);
  word-break: break-word;
}

.page-header-desc {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  width: 100%;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 641px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-5);
  }
}

@media (min-width: 1025px) {
  .dashboard-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--space-6);
  }

  .dashboard-grid-wide {
    grid-column: 1 / -1;
  }

  .page-header {
    flex-direction: row;
    align-items: center;
  }

  .page-header-actions {
    width: auto;
  }
}
</style>

