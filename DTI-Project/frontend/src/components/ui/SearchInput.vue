<template>
  <div class="search-box">
    <label :for="id" class="sr-only">{{ accessibleLabel }}</label>
    <ui-icon name="search" size="16" />
    <input
      :id="id"
      :name="resolvedName"
      :value="modelValue"
      type="text"
      :placeholder="placeholder"
      class="search-input"
      @input="$emit('update:modelValue', $event.target.value)"
      @keydown.enter="$emit('search')"
      @keydown.escape="$emit('clear')"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import UiIcon from './UiIcon.vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search...' },
  label: { type: String, default: '' },
  name: { type: String, default: '' },
  id: { type: String, default: () => `search-input-${Math.random().toString(36).substr(2, 9)}` },
})

defineEmits(['update:modelValue', 'search', 'clear'])

const accessibleLabel = computed(() => props.label || props.placeholder || 'Search')
const resolvedName = computed(() => props.name || props.id)
</script>

<style scoped>
.search-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1 1 16rem;
  min-width: 0;
  width: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius);
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  transition: all var(--transition-base);
}

.search-box:focus-within {
  border-color: var(--brand-navy-400);
  box-shadow: 0 0 0 3px rgba(46, 80, 128, 0.12);
}

.search-box svg {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: var(--text-base);
  outline: none;
  font-family: inherit;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

@media (max-width: 640px) {
  .search-box {
    padding: var(--space-2) var(--space-3);
  }
}
</style>
