<template>
  <div class="summary-cards">
    <div
      v-for="card in cards"
      :key="card.id"
      class="stat-card"
      :style="{ '--stat-accent': card.accentColor, '--stat-icon-bg': card.iconBg, '--stat-icon-color': card.iconColor }"
    >
      <div class="stat-card-icon" v-if="card.icon">
        <component :is="card.icon" :size="20" />
      </div>
      <div class="stat-card-label">{{ card.label }}</div>
      <div class="stat-card-value" :class="{ 'currency': card.type === 'currency' }">
        {{ card.value }}
      </div>
      <div class="stat-card-sub" v-if="card.change">
        <span :class="['change-indicator', card.change > 0 ? 'positive' : 'negative']">
          {{ card.change > 0 ? '↑' : '↓' }}
        </span>
        <span>{{ Math.abs(card.change) }}% from last period</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  cards: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

.change-indicator {
  font-weight: var(--weight-semibold);
}

.change-indicator.positive {
  color: var(--status-success-text);
}

.change-indicator.negative {
  color: var(--status-danger-text);
}

@media (min-width: 641px) {
  .summary-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1025px) {
  .summary-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
</style>