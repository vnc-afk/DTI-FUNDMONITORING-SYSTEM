<template>
  <div class="table-footer">
    <div class="table-footer-info">
      <span v-if="totalItems" class="text-sm text-muted">
        Showing {{ start }} to {{ end }} of {{ totalItems }} results
      </span>
    </div>
    <div class="table-footer-pagination">
      <button
        class="btn btn-sm btn-secondary"
        :disabled="currentPage === 1"
        @click="$emit('prev-page')"
      >
        Previous
      </button>
      <span class="pagination-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        class="btn btn-sm btn-secondary"
        :disabled="currentPage === totalPages"
        @click="$emit('next-page')"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  totalItems: { type: Number, default: 0 },
})

const emit = defineEmits(['prev-page', 'next-page'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize))
const start = computed(() => (props.currentPage - 1) * props.pageSize + 1)
const end = computed(() => Math.min(props.currentPage * props.pageSize, props.totalItems))
</script>

<style scoped>
.table-footer {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: space-between;
  padding: var(--space-4);
  border-top: 1px solid var(--border-subtle);
  background: var(--surface-subtle);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  gap: var(--space-4);
}

.table-footer-info {
  flex: 1;
}

.table-footer-pagination {
  display: flex;
  align-items: stretch;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
}

.text-sm {
  font-size: var(--text-sm);
}

.text-muted {
  color: var(--text-muted);
}

@media (min-width: 641px) {
  .table-footer {
    align-items: center;
    flex-direction: row;
  }

  .table-footer-pagination {
    align-items: center;
    justify-content: flex-end;
  }
}

@media (max-width: 640px) {
  .table-footer-pagination .btn {
    width: 100%;
  }

  .pagination-info {
    text-align: center;
    width: 100%;
  }
}
</style>
