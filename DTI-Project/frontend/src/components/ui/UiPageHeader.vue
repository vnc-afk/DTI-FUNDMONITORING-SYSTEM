<template>
  <div class="page-header">
    <div class="page-header-info">
      <div class="page-header-eyebrow" v-if="eyebrow">{{ eyebrow }}</div>
      <h1 class="page-header-title">{{ title }}</h1>
      <p class="page-header-desc" v-if="description">{{ description }}</p>
    </div>
    <div class="page-header-actions" v-if="$slots.default">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
})
</script>

<style scoped></style>
