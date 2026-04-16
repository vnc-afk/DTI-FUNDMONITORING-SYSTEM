<template>
  <div class="filter-chips" role="group" :aria-label="ariaLabel || 'Filter options'">
    <button
      v-for="chip in chips"
      :key="`chip-${chip.value}`"
      type="button"
      class="filter-chip"
      :class="{ active: modelValue === chip.value }"
      :title="`${chip.label}${modelValue === chip.value ? ' (selected)' : ''}`"
      :aria-pressed="modelValue === chip.value"
      @click="handleChipClick(chip.value)"
    >
      {{ chip.label }}
      <span v-if="modelValue === chip.value" class="chip-indicator" aria-hidden="true">✓</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({  // ← capture the return value
  modelValue: { type: String, default: '' },
  chips: {
    type: Array,
    required: true,
    validator: (value) => value.every(chip => chip.value && chip.label),
  },
  ariaLabel: { type: String, default: '' },
  toggleMode: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

function handleChipClick(chipValue) {
  if (props.toggleMode && props.modelValue === chipValue) {  // ← use props.*
    emit('update:modelValue', '')
  } else {
    emit('update:modelValue', chipValue)
  }
}
</script>


<style scoped>
.filter-chips {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  align-items: center;
  min-width: 0;
}

.filter-chip {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  user-select: none;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  min-height: 40px;
}

.filter-chip:hover {
  border-color: var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
}

.filter-chip.active {
  background: var(--brand-navy-dim);
  border-color: var(--brand-navy-strong);
  color: var(--brand-navy-strong);
  font-weight: 700;
}

.filter-chip:focus {
  outline: 2px solid var(--brand-navy-400);
  outline-offset: 2px;
}

.filter-chip:active {
  transform: scale(0.98);
}

.chip-indicator {
  display: inline-block;
  font-size: 0.75em;
  font-weight: 900;
  margin-left: var(--space-1);
}

@media (max-width: 640px) {
  .filter-chips {
    width: 100%;
  }

  .filter-chip {
    min-height: 44px;
    padding: var(--space-2) var(--space-3);
  }
}
</style>
