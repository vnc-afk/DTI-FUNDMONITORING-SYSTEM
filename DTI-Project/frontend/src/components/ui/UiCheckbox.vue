<template>
  <div class="checkbox-wrapper">
    <input
      type="checkbox"
      :id="id"
      :checked="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.checked)"
      class="checkbox"
    />
    <label :for="id" class="checkbox-label" v-if="label">{{ label }}</label>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  label: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  id: { type: String, default: () => `checkbox-${Math.random().toString(36).substr(2, 9)}` },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--surface-base);
  transition: all var(--duration-fast) var(--ease-out);
  appearance: none;
  -webkit-appearance: none;
}

.checkbox:checked {
  background: var(--brand-navy-700);
  border-color: var(--brand-navy-700);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3E%3Cpath d='M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z'/%3E%3C/svg%3E");
  background-size: 100%;
  background-position: center;
  background-repeat: no-repeat;
}

.checkbox:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.checkbox:focus {
  outline: 2px solid var(--brand-navy-400);
  outline-offset: 2px;
}

.checkbox-label {
  font-size: var(--text-base);
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
}
</style>
 