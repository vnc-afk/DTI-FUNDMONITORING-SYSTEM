<template>
  <div class="data-table-wrapper" tabindex="0" role="region" :aria-label="ariaLabel">
    <table class="data-table">
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.id"
            :class="[{ numeric: col.numeric, sortable: isSortable(col), sorted: isSorted(col) }]"
            :aria-sort="ariaSort(col)"
          >
            <button
              v-if="isSortable(col)"
              type="button"
              class="sort-header"
              @click="handleSort(col)"
            >
              <span>{{ col.label }}</span>
              <span class="sort-indicator" :class="{ active: isSorted(col) }">{{ sortIndicator(col) }}</span>
            </button>
            <span v-else>{{ col.label }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="displayedRows.length === 0">
          <td :colspan="columns.length" class="text-center text-muted">
            No data
          </td>
        </tr>
        <tr v-for="(row, idx) in displayedRows" :key="idx">
          <td v-for="col in columns" :key="col.id" :class="{ 'numeric': col.numeric }">
            <slot :name="`cell-${col.id}`" :row="row" :col="col" :value="row[col.id]" :index="idx">
              <slot :row="row" :col="col" :value="row[col.id]" :index="idx">
                {{ row[col.id] }}
              </slot>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    // { id: 'name', label: 'Name', numeric: false }
  },
  rows: {
    type: Array,
    default: () => [],
  },
  ariaLabel: {
    type: String,
    default: 'Data table',
  },
  sortBy: {
    type: String,
    default: '',
  },
  sortDir: {
    type: String,
    default: 'asc',
  },
})

const emit = defineEmits(['sort'])

const localSortBy = ref('')
const localSortDir = ref('asc')

const hasExternalSort = computed(() => Boolean(props.sortBy))

const activeSortBy = computed(() => (hasExternalSort.value ? props.sortBy : localSortBy.value))

const activeSortDir = computed(() => {
  const dir = hasExternalSort.value ? props.sortDir : localSortDir.value
  return dir === 'desc' ? 'desc' : 'asc'
})

const displayedRows = computed(() => {
  const sortKey = activeSortBy.value
  const column = props.columns.find((col) => col.id === sortKey)
  if (!sortKey || !column || !isSortable(column)) {
    return props.rows
  }

  const direction = activeSortDir.value === 'desc' ? -1 : 1
  return [...props.rows].sort((rowA, rowB) => direction * compareValues(rowA?.[sortKey], rowB?.[sortKey]))
})

function isSortable(column) {
  if (!column || !column.id) return false
  if (column.sortable === false) return false
  return column.id !== 'actions'
}

function isSorted(column) {
  return Boolean(column && activeSortBy.value && column.id === activeSortBy.value)
}

function ariaSort(column) {
  if (!isSortable(column)) return undefined
  if (!isSorted(column)) return 'none'
  return activeSortDir.value === 'desc' ? 'descending' : 'ascending'
}

function sortIndicator(column) {
  if (!isSorted(column)) return '↕'
  return activeSortDir.value === 'desc' ? '↓' : '↑'
}

function handleSort(column) {
  if (!isSortable(column)) return

  const nextDir = isSorted(column) && activeSortDir.value === 'asc' ? 'desc' : 'asc'

  if (!hasExternalSort.value) {
    localSortBy.value = column.id
    localSortDir.value = nextDir
  }

  emit('sort', { column: column.id, direction: nextDir })
}

function compareValues(a, b) {
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1

  if (typeof a === 'number' && typeof b === 'number') {
    return a - b
  }

  const dateA = new Date(a)
  const dateB = new Date(b)
  const hasValidDates = !Number.isNaN(dateA.getTime()) && !Number.isNaN(dateB.getTime())
  if (hasValidDates) {
    return dateA.getTime() - dateB.getTime()
  }

  return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: 'base' })
}
</script>

<style scoped>
.data-table-wrapper {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-sm);
}

.data-table {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  background: var(--surface-base);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
}

.data-table thead th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  background: var(--surface-subtle);
  border-bottom: 1px solid var(--border-default);
  white-space: nowrap;
}

.data-table thead th.sortable {
  padding: 0;
}

.sort-header {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: var(--space-2);
  border: none;
  background: transparent;
  color: inherit;
  padding: var(--space-3) var(--space-4);
  font: inherit;
  letter-spacing: inherit;
  text-transform: inherit;
  cursor: pointer;
}

.sort-header:focus-visible {
  outline: 2px solid var(--brand-navy-500);
  outline-offset: -2px;
}

.sort-indicator {
  color: var(--text-muted);
  font-size: var(--text-sm);
  line-height: 1;
}

.sort-indicator.active {
  color: var(--brand-navy-700);
}

.data-table thead th:first-child { border-radius: var(--radius-xl) 0 0 0; }
.data-table thead th:last-child  { border-radius: 0 var(--radius-xl) 0 0; }

.data-table tbody tr {
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--duration-fast) var(--ease-out);
}

.data-table tbody tr:last-child { border-bottom: none; }
.data-table tbody tr:hover { background: var(--surface-subtle); }

.data-table tbody td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--weight-regular);
  color: var(--text-primary);
  line-height: var(--leading-normal);
  vertical-align: middle;
  min-width: 0;
}

.data-table tbody td.numeric {
  text-align: right;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  color: var(--text-primary);
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .data-table thead th,
  .data-table tbody td {
    padding: var(--space-2) var(--space-3);
  }

  .data-table {
    font-size: var(--text-sm);
  }
}
</style>