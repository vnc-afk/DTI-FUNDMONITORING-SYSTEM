<template>
  <div class="form-group">
    <label v-if="label" :for="id" class="form-label" :class="{ required: required }">
      {{ label }}
    </label>
    <select
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :class="['select', { 'error': error }]"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" v-if="placeholder" disabled>{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="form-error">{{ error }}</p>
    <p v-else-if="hint" class="form-hint">{{ hint }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  id: { type: String, default: () => `select-${Math.random().toString(36).substr(2, 9)}` },
})

defineEmits(['update:modelValue'])
</script>

<style scoped></style>