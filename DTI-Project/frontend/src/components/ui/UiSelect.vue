<template>
  <div class="form-group">
    <label v-if="label" :for="id" class="form-label" :class="{ required: required }">
      {{ label }}
    </label>

    <div
      v-if="searchable"
      class="ui-select-combobox"
      @keydown="handleKeydown"
    >
      <input
        :id="id"
        ref="searchInputRef"
        :value="searchableText"
        type="text"
        :placeholder="resolvedSearchPlaceholder"
        :disabled="disabled"
        :required="required"
        :class="['input', 'ui-select-combobox__input', { 'error': error }]"
        autocomplete="off"
        role="combobox"
        :aria-expanded="isDropdownOpen"
        :aria-controls="dropdownId"
        :aria-autocomplete="'list'"
        @focus="openDropdown"
        @input="handleSearchableInput"
        @blur="handleSearchableBlur"
      />

      <button
        type="button"
        class="ui-select-combobox__toggle"
        :disabled="disabled"
        aria-label="Toggle options"
        @mousedown.prevent
        @click="toggleDropdown"
      >
        <span class="ui-select-combobox__caret" />
      </button>

      <ul
        v-if="isDropdownOpen"
        :id="dropdownId"
        class="ui-select-combobox__menu"
        role="listbox"
      >
        <li v-if="!filteredOptions.length" class="ui-select-combobox__empty">
          {{ noResultsText }}
        </li>
        <li
          v-for="(opt, index) in filteredOptions"
          :key="opt.value"
          class="ui-select-combobox__option"
          :class="{
            'is-highlighted': index === highlightedIndex,
            'is-selected': String(opt.value) === String(modelValue),
          }"
          role="option"
          :aria-selected="String(opt.value) === String(modelValue)"
          @mousedown.prevent="selectOption(opt)"
        >
          {{ opt.label }}
        </li>
      </ul>
    </div>

    <select
      v-else
      :id="id"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :class="['select', { 'error': error }]"
      @change="handleChange"
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
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  searchable: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: '' },
  noResultsText: { type: String, default: 'No matching options' },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  id: { type: String, default: () => `select-${Math.random().toString(36).substr(2, 9)}` },
})

const emit = defineEmits(['update:modelValue'])
const searchableText = ref('')
const searchInputRef = ref(null)
const isDropdownOpen = ref(false)
const highlightedIndex = ref(-1)

const dropdownId = computed(() => `${props.id}-listbox`)

const resolvedSearchPlaceholder = computed(() => {
  if (props.searchPlaceholder) {
    return props.searchPlaceholder
  }
  if (props.placeholder) {
    return props.placeholder
  }
  return 'Search options'
})

const filteredOptions = computed(() => {
  const query = String(searchableText.value || '').trim().toLowerCase()
  if (!query) {
    return props.options
  }

  return props.options.filter((option) =>
    String(option?.label || '').toLowerCase().includes(query)
  )
})

watch(
  [() => props.modelValue, () => props.options],
  () => {
    if (!props.searchable) {
      return
    }

    if (isDropdownOpen.value) {
      return
    }

    const selected = props.options.find(
      (option) => String(option?.value) === String(props.modelValue)
    )
    searchableText.value = selected ? String(selected.label) : ''
  },
  { immediate: true }
)

function handleChange(event) {
  const value = event?.target?.value ?? ''
  emit('update:modelValue', value)
}

function findOptionByLabel(label) {
  const normalized = String(label || '').trim().toLowerCase()
  if (!normalized) {
    return null
  }

  return (
    props.options.find((option) => String(option?.label || '').toLowerCase() === normalized) ||
    null
  )
}

function openDropdown() {
  if (props.disabled) {
    return
  }

  isDropdownOpen.value = true
  highlightedIndex.value = filteredOptions.value.length ? 0 : -1
}

function closeDropdown() {
  isDropdownOpen.value = false
  highlightedIndex.value = -1
}

function selectOption(option) {
  searchableText.value = String(option?.label || '')
  emit('update:modelValue', option?.value ?? '')
  closeDropdown()
}

function handleSearchableInput(event) {
  const text = event?.target?.value ?? ''
  searchableText.value = text
  isDropdownOpen.value = true
  highlightedIndex.value = filteredOptions.value.length ? 0 : -1

  if (!String(text).trim()) {
    emit('update:modelValue', '')
    return
  }

  const matchedOption = findOptionByLabel(text)
  if (matchedOption) {
    emit('update:modelValue', matchedOption.value)
  }
}

function handleSearchableBlur() {
  setTimeout(() => {
    if (!String(searchableText.value).trim()) {
      emit('update:modelValue', '')
      searchableText.value = ''
      closeDropdown()
      return
    }

    const matchedOption = findOptionByLabel(searchableText.value)
    if (matchedOption) {
      searchableText.value = String(matchedOption.label)
      emit('update:modelValue', matchedOption.value)
      closeDropdown()
      return
    }

    const selected = props.options.find(
      (option) => String(option?.value) === String(props.modelValue)
    )

    searchableText.value = selected ? String(selected.label) : ''
    if (!selected) {
      emit('update:modelValue', '')
    }
    closeDropdown()
  }, 120)
}

function toggleDropdown() {
  if (props.disabled) {
    return
  }

  if (isDropdownOpen.value) {
    closeDropdown()
    return
  }

  openDropdown()
  searchInputRef.value?.focus()
}

function handleKeydown(event) {
  if (!props.searchable || props.disabled) {
    return
  }

  const total = filteredOptions.value.length

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    if (!isDropdownOpen.value) {
      openDropdown()
      return
    }
    if (!total) {
      return
    }
    highlightedIndex.value = (highlightedIndex.value + 1 + total) % total
    return
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (!isDropdownOpen.value) {
      openDropdown()
      return
    }
    if (!total) {
      return
    }
    highlightedIndex.value = (highlightedIndex.value - 1 + total) % total
    return
  }

  if (event.key === 'Enter') {
    if (!isDropdownOpen.value) {
      return
    }
    event.preventDefault()
    if (highlightedIndex.value >= 0 && highlightedIndex.value < total) {
      selectOption(filteredOptions.value[highlightedIndex.value])
    }
    return
  }

  if (event.key === 'Escape') {
    closeDropdown()
  }
}
</script>

<style scoped>
.ui-select-combobox {
  position: relative;
}

.ui-select-combobox__input {
  padding-right: 2.25rem;
}

.ui-select-combobox__toggle {
  position: absolute;
  top: 50%;
  right: var(--space-2);
  transform: translateY(-50%);
  border: none;
  background: transparent;
  padding: 0;
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.ui-select-combobox__caret {
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid var(--text-secondary);
}

.ui-select-combobox__menu {
  position: absolute;
  z-index: 20;
  left: 0;
  right: 0;
  margin: var(--space-1) 0 0;
  padding: var(--space-1) 0;
  list-style: none;
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  max-height: 220px;
  overflow-y: auto;
  box-shadow: var(--shadow-md);
}

.ui-select-combobox__option,
.ui-select-combobox__empty {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.ui-select-combobox__option {
  cursor: pointer;
  color: var(--text-primary);
}

.ui-select-combobox__option.is-highlighted,
.ui-select-combobox__option:hover {
  background: var(--surface-subtle);
}

.ui-select-combobox__option.is-selected {
  font-weight: var(--weight-semibold);
}

.ui-select-combobox__empty {
  color: var(--text-secondary);
}
</style>