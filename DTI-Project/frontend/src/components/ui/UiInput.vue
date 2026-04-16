<template>
  <div class="form-group">
    <label v-if="label" :for="id" class="form-label" :class="{ required: required }">
      {{ label }}
    </label>
    <div class="ui-input__control" :class="{ 'ui-input__control--with-suffix': hasSuffix }">
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :name="name || undefined"
        :autocomplete="autocomplete || undefined"
        :class="['input', { 'error': error }, { 'ui-input__field--with-suffix': hasSuffix }]"
        @input="handleInput"
        @blur="emit('blur')"
        @focus="emit('focus')"
      />

      <div v-if="hasSuffix" class="ui-input__suffix">
        <slot name="suffix" />
      </div>
    </div>
    <p v-if="error" class="form-error">{{ error }}</p>
    <p v-else-if="hint" class="form-hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  modelModifiers: { type: Object, default: () => ({}) },
  type: { type: String, default: 'text' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  name: { type: String, default: '' },
  autocomplete: { type: String, default: '' },
  id: { type: String, default: () => `input-${Math.random().toString(36).substr(2, 9)}` },
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const slots = useSlots()
const hasSuffix = computed(() => Boolean(slots.suffix))

function handleInput(event) {
  const nextValue = event?.target?.value ?? ''
  const shouldCoerceNumber = props.type === 'number' || Boolean(props.modelModifiers?.number)

  if (shouldCoerceNumber) {
    if (nextValue === '') {
      emit('update:modelValue', '')
      return
    }

    const parsedValue = Number(nextValue)
    emit('update:modelValue', Number.isNaN(parsedValue) ? nextValue : parsedValue)
    return
  }

  emit('update:modelValue', nextValue)
}
</script>

<style scoped>
.ui-input__control {
  position: relative;
  display: flex;
  align-items: center;
}

.ui-input__suffix {
  position: absolute;
  right: var(--space-2);
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
}

.ui-input__field--with-suffix {
  padding-right: calc(var(--space-3) + 2.5rem);
}
</style>