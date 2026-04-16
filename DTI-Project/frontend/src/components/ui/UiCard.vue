<template>
  <div class="card" :class="{ 'card-interactive': interactive }" @click="() => interactive && emit('click')">
    <div class="card-header" v-if="$slots.header || title">
      <div>
        <h3 v-if="title" class="card-title">{{ title }}</h3>
      </div>
      <slot name="header" />
    </div>
    <div class="card-body">
      <slot />
    </div>
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  interactive: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])
</script>

<style scoped>
.card-interactive {
  cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

</style>
 