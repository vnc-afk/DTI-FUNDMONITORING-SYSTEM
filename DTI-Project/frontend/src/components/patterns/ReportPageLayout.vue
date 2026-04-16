<template>
  <div class="report-page" :class="rootClass">
    <div v-if="showDefaultHeader" class="page-header">
      <div class="page-header-info">
        <div class="page-header-eyebrow" v-if="eyebrow">{{ eyebrow }}</div>
        <h1 class="page-header-title">{{ title }}</h1>
        <p class="page-header-desc" v-if="description">{{ description }}</p>
      </div>
      <div class="page-header-actions">
        <slot name="header-actions" />
      </div>
    </div>

    <div v-if="showToolbar" class="report-toolbar">
      <slot name="toolbar" />
    </div>

    <div class="report-content">
      <slot />
    </div>

    <div class="report-footer" v-if="showFooterArea">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  showFooter: { type: Boolean, default: false },
  rootClass: { type: String, default: '' },
})

const slots = useSlots()

const showDefaultHeader = computed(() => Boolean(props.title || props.description || props.eyebrow))
const showToolbar = computed(() => Boolean(slots.toolbar))
const showFooterArea = computed(() => Boolean(props.showFooter || slots.footer))
</script>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  min-width: 0;

}

.report-toolbar {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
  align-items: center;
}

.report-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.report-footer {
  display: flex;
  gap: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.page-header-info {
  min-width: 0;
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

@media (min-width: 641px) {
  .page-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }

  .page-header-actions {
    width: auto;
    justify-content: flex-end;
  }
}
</style>
