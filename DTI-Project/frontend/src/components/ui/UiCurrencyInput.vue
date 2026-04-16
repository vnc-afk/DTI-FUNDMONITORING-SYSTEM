<template>
  <div class="form-group">
    <label v-if="label" :for="id" class="form-label">{{ label }}</label>
    <div class="currency-input">
      <span class="currency-prefix" aria-hidden="true">₱</span>
      <input
        :id="id"
        :name="resolvedName"
        :value="modelValue"
        type="number"
        min="0"
        step="0.01"
        class="input currency-field"
        :class="{ error, readonly }"
        :placeholder="placeholder"
        :readonly="readonly"
        :required="required"
        @input="$emit('update:modelValue', parseFloat($event.target.value) || 0)"
      />
    </div>
    <p v-if="error" class="form-error">{{ error }}</p>
    <p v-if="hint" class="form-hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: 0,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  name: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: () => `currency-input-${Math.random().toString(36).substr(2, 9)}`,
  },
})

defineEmits(['update:modelValue'])

const resolvedName = computed(() => props.name || props.id)
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.currency-input {
  position: relative;
  display: flex;
  align-items: center;
}

.currency-prefix {
  position: absolute;
  left: var(--space-3);
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
  pointer-events: none;
}

.currency-field {
  width: 100%;
  padding: var(--space-2) var(--space-3) var(--space-2) var(--space-8);
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--surface-base);
  color: var(--text-primary);
  font-size: var(--text-sm);
  transition: border-color var(--duration-fast) var(--ease-out);
}

.currency-field:focus {
  outline: none;
  border-color: var(--brand-navy-600);
  box-shadow: 0 0 0 3px var(--brand-navy-100);
}

.currency-field.error {
  border-color: var(--status-danger-border);
}


.form-error {
  font-size: var(--text-xs);
  color: var(--status-danger-text);
  margin: 0;
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin: 0;
}
</style>
