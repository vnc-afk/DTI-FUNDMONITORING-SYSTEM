<template>
  <div class="quarterly-acc">
    <div v-for="item in items" :key="item.id" class="acc-item" :class="{ open: isOpen(item.id) }">
      <div class="acc-header" @click="toggleItem(item.id)">
        <div class="acc-header-left">
          <slot name="header-left" :item="item">
            <div class="acc-q-label">{{ item.label }}</div>
            <div v-if="item.subtitle" class="q-range">{{ item.subtitle }}</div>
          </slot>
        </div>

        <div class="acc-header-right">
          <slot name="header-right" :item="item">
            <UiBadge 
              v-if="item.badge" 
              :text="item.badge"
              :variant="item.badgeActive ? 'success' : 'warning'"
              size="sm"
              pill
            />
            <div v-if="item.total !== undefined" :class="['q-grand-total', { empty: item.total === 0 }]">
              {{ item.totalDisplay || item.total }}
            </div>
          </slot>
          <div class="acc-chevron">▼</div>
        </div>
      </div>

      <div class="acc-body">
        <slot name="body" :item="item" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UiBadge from './UiBadge.vue'

defineProps({
  items: {
    type: Array,
    required: true,
    // [{ id: 'q1', label: 'Q1', subtitle: 'Jan - Mar', badge: 'Active', badgeActive: true, total: 1000, totalDisplay: '₱ 1,000.00' }, ...]
  },
  defaultOpen: {
    type: Array,
    default: () => [],
  },
})

const openItems = ref(new Set())

const isOpen = (id) => openItems.value.has(id)

const toggleItem = (id) => {
  if (openItems.value.has(id)) {
    openItems.value.delete(id)
  } else {
    openItems.value.add(id)
  }
}
</script>

<style scoped>
@import '@/assets/css/patterns/reports.css';

/* Label for accordion items */
.acc-q-label {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
}
</style>