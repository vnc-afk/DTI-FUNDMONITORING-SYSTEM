<template>
  <div>
    <!-- Page Header -->
    <ui-page-header :title="title" :description="description" :eyebrow="eyebrow">
      <slot name="header-actions">
        <router-link v-if="addRoute" :to="addRoute" class="btn btn-primary">
          <ui-icon name="plus" size="14" />
          {{ addLabel || 'Add New' }}
        </router-link>
      </slot>
    </ui-page-header>

    <!-- Summary cards slot -->
    <slot name="summary" />

    <!-- Toolbar -->
    <ui-toolbar>
      <template #filters>
        <!-- Search -->
        <search-input
          :model-value="internalSearch"
          :placeholder="`Search ${title.toLowerCase()}…`"
          @update:model-value="internalSearch = $event"
        />

        <!-- Filter slots -->
        <slot name="filters" />

        <!-- Active filter chips -->
        <filter-chips
          v-if="activeFilters.length"
          :chips="activeFilterChips"
          @update:model-value="$emit('remove-filter', arguments)"
        />
      </template>

      <slot name="toolbar-actions" />

      <!-- Bulk actions (shown when rows selected) -->
      <template v-if="selectedCount > 0">
        <div class="toolbar-divider"></div>
        <span class="text-sm text-secondary">{{ selectedCount }} selected</span>
        <button class="btn btn-sm btn-danger" @click="$emit('bulk-delete')">
          <ui-icon name="trash-2" size="14" />
          Delete
        </button>
        <button class="btn btn-sm btn-secondary" @click="$emit('bulk-archive')">Archive</button>
      </template>

      <!-- Export -->
      <button class="btn btn-sm btn-secondary" @click="$emit('export')">
        <ui-icon name="download" size="14" />
        Export
      </button>
    </ui-toolbar>

    <!-- Loading State -->
    <loading-state v-if="loading" :message="`Loading ${title.toLowerCase()}…`" />

    <!-- Table -->
    <ui-table
      v-else
      :columns="tableColumns"
      :rows="tableRows"
      :sort-by="sortBy"
      :sort-dir="sortDir"
      @sort="$emit('sort', $event)"
    >
      <template #default="{ row, col }">
        <slot :name="`cell-${col.id}`" :row="row" :value="row[col.id]">
          {{ row[col.id] }}
        </slot>
      </template>
    </ui-table>

    <!-- No Results State -->
    <ui-no-results
      v-if="!loading && rowCount === 0"
      title="No records found"
      :description="emptyMessage || 'Try adjusting your search or filters.'"
    />

    <!-- Table Footer / Pagination -->
    <ui-table-footer
      v-if="!loading && rowCount > 0"
      :current-page="currentPage"
      :page-size="pageSize"
      :total-items="total"
      @prev-page="$emit('page', currentPage - 1)"
      @next-page="$emit('page', currentPage + 1)"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import UiPageHeader from '@/components/ui/UiPageHeader.vue'
import UiToolbar from '@/components/ui/UiToolbar.vue'
import UiTable from '@/components/ui/UiTable.vue'
import UiTableFooter from '@/components/ui/UiTableFooter.vue'
import UiNoResults from '@/components/ui/UiNoResults.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import FilterChips from '@/components/ui/FilterChips.vue'
import LoadingState from '@/components/ui/LoadingState.vue'

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  addRoute: String,
  addLabel: String,
  columns: { type: Array, default: () => [] },
  loading: Boolean,
  rowCount: { type: Number, default: 0 },
  rows: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  sortBy: { type: String, default: '' },
  sortDir: { type: String, default: 'asc' },
  selectedCount: { type: Number, default: 0 },
  allSelected: Boolean,
  activeFilters: { type: Array, default: () => [] },
  emptyMessage: String,
})

defineEmits(['sort', 'page', 'select-all', 'bulk-delete', 'bulk-archive', 'export', 'remove-filter', 'update:search'])

const internalSearch = ref('')

const tableColumns = computed(() =>
  props.columns.map(col => ({
    id: col.key || col.id,
    label: col.label,
    numeric: col.numeric,
    width: col.width,
    sortable: col.sortable,
  }))
)

const tableRows = computed(() => props.rows)

const activeFilterChips = computed(() =>
  props.activeFilters.map((filter, idx) => ({
    value: idx.toString(),
    label: `${filter.label}: ${filter.value}`,
  }))
)
</script>

<style scoped>
.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--border-subtle);
}

.text-sm {
  font-size: var(--text-sm);
}

.text-secondary {
  color: var(--text-secondary);
}
</style>