<template>
  <component :is="iconComponent" :size="size" :stroke-width="strokeWidth" :class="iconClass" />
</template>

<script setup>
import { computed } from 'vue'
import * as LucideIcons from 'lucide-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  size: {
    type: [Number, String],
    default: 24,
  },
  class: {
    type: String,
    default: '',
  },
  strokeWidth: {
    type: Number,
    default: 2,
  },
})

const iconComponent = computed(() => {
  // Convert kebab-case to PascalCase
  const pascalCase = props.name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('')
  
  return LucideIcons[pascalCase] || LucideIcons.AlertCircle
})

const iconClass = computed(() => {
  return `lucide-icon ${props.class}`
})
</script>

<style scoped>
.lucide-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
