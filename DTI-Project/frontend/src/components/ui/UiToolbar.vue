<template>
  <div class="toolbar">
    <div class="toolbar-filters">
      <slot name="filters" />
    </div>
    <div class="toolbar-actions">
      <slot />
    </div>
  </div>
</template>

<script setup>
// Empty setup for now
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-4);
}

.toolbar-filters {
  display: flex;
  gap: var(--space-3);
  align-items: stretch;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.toolbar-actions {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  flex-wrap: wrap;
  min-width: 0;
  width: 100%;
  justify-content: flex-end;
}

@media (min-width: 641px) {
  .toolbar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .toolbar-actions {
    width: auto;
  }
}
</style>
