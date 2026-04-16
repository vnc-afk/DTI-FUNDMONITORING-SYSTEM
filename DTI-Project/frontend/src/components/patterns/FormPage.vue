<template>
  <div class="form-page" :class="rootClass">
    <template v-if="hasHeaderSlot">
      <slot name="header" />
    </template>

    <div v-else-if="showDefaultHeader" class="page-header">
      <div class="page-header-info">
        <div class="page-header-eyebrow" v-if="eyebrow">{{ eyebrow }}</div>
        <h1 class="page-header-title">{{ title }}</h1>
        <p class="page-header-desc" v-if="description">{{ description }}</p>
      </div>
    </div>

    <template v-if="hasCardSlot">
      <slot name="card" />
    </template>

    <form v-else @submit.prevent="handleSubmit" class="form-container" novalidate>
      <div class="form-content" :class="{ 'form-content--flush': cardPadding === 'none' }">
        <slot />
      </div>

      <div class="form-footer">
        <button type="button" class="btn btn-secondary" @click="handleCancel">
          {{ cancelLabel }}
        </button>
        <button type="submit" class="btn btn-primary" :disabled="disabled">
          {{ submitLabel }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  submitLabel: { type: String, default: 'Save' },
  cancelLabel: { type: String, default: 'Cancel' },
  disabled: { type: Boolean, default: false },
  rootClass: { type: String, default: '' },
  cardPadding: { type: String, default: 'normal' },
})

const emit = defineEmits(['submit', 'cancel'])

const slots = useSlots()

const hasHeaderSlot = computed(() => Boolean(slots.header))
const hasCardSlot = computed(() => Boolean(slots.card))
const showDefaultHeader = computed(() => Boolean(props.title || props.description || props.eyebrow))

const handleSubmit = () => {
  emit('submit')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.form-page {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.page-header {
  margin-bottom: var(--space-2);
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
  margin: 0 0 var(--space-2) 0;
  line-height: var(--leading-tight);
  word-break: break-word;
}

.page-header-desc {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

.form-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.form-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.form-content--flush {
  padding: 0;
}

.form-footer {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

@media (max-width: 640px) {
  .form-footer {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}

@media (min-width: 641px) {
  .page-header-title {
    font-size: var(--text-3xl);
  }
}
</style>
