<template>
  <div class="summary-page">
    <!-- Header -->
    <header class="page-header">
      <div class="page-header-info">
        <div class="page-header-eyebrow">
          <span class="eyebrow-dot"></span>
          <span>Live Overview</span>
        </div>
        <h1 class="page-header-title">Activity Summary</h1>
        <p class="page-header-desc">System-wide activity statistics and insights across all users and models</p>
      </div>
      <RouterLink to="/activity-logs" class="btn-primary-action">
        <ui-icon name="list-ul" size="18" />
        <span>View All Logs</span>
        <ui-icon name="arrow-right" class="btn-arrow" />
      </RouterLink>
    </header>

    <!-- KPI Cards -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-card-inner">
          <div class="kpi-icon kpi-icon--total">
            <ui-icon name="layers" />
          </div>
          <div class="kpi-body">
            <span class="kpi-label">Total Activities</span>
            <span class="kpi-value">{{ formatNumber(summary.total_logs) }}</span>
            <span class="kpi-note">All time</span>
          </div>
        </div>
        <div class="kpi-bar kpi-bar--full"></div>
      </div>

      <div class="kpi-card kpi-card--today">
        <div class="kpi-card-inner">
          <div class="kpi-icon kpi-icon--today">
            <ui-icon name="sun" />
          </div>
          <div class="kpi-body">
            <span class="kpi-label">Today</span>
            <span class="kpi-value">{{ formatNumber(summary.today_logs) }}</span>
            <span class="kpi-note">Activities today</span>
          </div>
        </div>
        <div class="kpi-bar" :style="{ width: todayPercent + '%' }"></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-inner">
          <div class="kpi-icon kpi-icon--week">
            <ui-icon name="calendar" />
          </div>
          <div class="kpi-body">
            <span class="kpi-label">Last 7 Days</span>
            <span class="kpi-value">{{ formatNumber(summary.week_logs) }}</span>
            <span class="kpi-note">Weekly activities</span>
          </div>
        </div>
        <div class="kpi-bar" :style="{ width: weekPercent + '%' }"></div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-inner">
          <div class="kpi-icon kpi-icon--month">
            <ui-icon name="calendar" />
          </div>
          <div class="kpi-body">
            <span class="kpi-label">Last 30 Days</span>
            <span class="kpi-value">{{ formatNumber(summary.month_logs) }}</span>
            <span class="kpi-note">Monthly activities</span>
          </div>
        </div>
        <div class="kpi-bar" :style="{ width: monthPercent + '%' }"></div>
      </div>
    </section>

    <!-- Charts Grid -->
    <div class="chart-grid">
      <!-- Actions Breakdown -->
      <div class="chart-card">
        <div class="chart-card-header">
          <div class="chart-card-title">
            <ui-icon name="bar-chart-3" />
            <h2>Actions Breakdown</h2>
          </div>
          <span class="chart-card-count">{{ summary.actions_breakdown.length }} types</span>
        </div>
        <div class="chart-card-body">
          <template v-if="summary.actions_breakdown.length">
            <div
              v-for="action in summary.actions_breakdown"
              :key="action.action"
              class="bar-row"
            >
              <div class="bar-row-header">
                <span class="action-badge" :class="`action-badge--${action.action.toLowerCase()}`">
                  {{ action.action }}
                </span>
                <span class="bar-value">{{ formatNumber(action.count) }}</span>
              </div>
              <div class="progress-track">
                <div
                  class="progress-fill"
                  :class="`progress-fill--${action.action.toLowerCase()}`"
                  :style="{ width: `${toPercent(action.count)}%` }"
                  role="progressbar"
                  :aria-valuenow="action.count"
                  aria-valuemin="0"
                  :aria-valuemax="summary.total_logs"
                >
                  <span v-if="toPercent(action.count) > 12" class="progress-pct">
                    {{ toPercent(action.count) }}%
                  </span>
                </div>
                <span v-if="toPercent(action.count) <= 12" class="progress-pct-outside">
                  {{ toPercent(action.count) }}%
                </span>
              </div>
            </div>
          </template>
          <div v-else class="empty-state">
            <ui-icon name="bar-chart-3" />
            <p>No data available</p>
          </div>
        </div>
      </div>

      <!-- Most Modified Models -->
      <div class="chart-card">
        <div class="chart-card-header">
          <div class="chart-card-title">
            <ui-icon name="database" />
            <h2>Most Modified Models</h2>
          </div>
          <span class="chart-card-count">{{ summary.modified_models.length }} models</span>
        </div>
        <div class="chart-card-body">
          <template v-if="summary.modified_models.length">
            <div
              v-for="(model, idx) in summary.modified_models"
              :key="model.model_name"
              class="rank-row"
            >
              <span class="rank-badge" :class="idx < 3 ? `rank-badge--top${idx + 1}` : ''">
                {{ idx + 1 }}
              </span>
              <div class="rank-info">
                <div class="rank-top">
                  <RouterLink
                    :to="`/activity-logs/model/${encodeURIComponent(model.model_name)}`"
                    class="rank-link"
                  >{{ model.model_name }}</RouterLink>
                  <strong class="rank-count">{{ formatNumber(model.count) }}</strong>
                </div>
                <div class="rank-track">
                  <div
                    class="rank-fill"
                    :style="{ width: `${toPercent(model.count)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="empty-state">
            <ui-icon name="database" />
            <p>No data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Users & Sensitive Activities Grid -->
    <div class="chart-grid">
      <!-- Most Active Users -->
      <div class="chart-card">
        <div class="chart-card-header">
          <div class="chart-card-title">
            <ui-icon name="users" />
            <h2>Most Active Users</h2>
          </div>
          <span class="chart-card-count">{{ summary.active_users.length }} users</span>
        </div>
        <div class="chart-card-body">
          <template v-if="summary.active_users.length">
            <div
              v-for="(user, idx) in summary.active_users"
              :key="user.user_id || user.username"
              class="rank-row rank-row--user"
            >
              <span class="rank-badge" :class="idx < 3 ? `rank-badge--top${idx + 1}` : ''">
                {{ idx + 1 }}
              </span>
              <div class="rank-info">
                <div class="rank-top">
                  <div class="user-identity">
                    <div class="user-avatar" :style="{ background: avatarColor(user.display_name) }">
                      {{ initials(user.display_name) }}
                    </div>
                    <RouterLink
                      :to="`/activity-logs/user/${user.user_id || 0}`"
                      class="rank-link"
                    >
                      {{ user.display_name }}
                      <small class="rank-handle">@{{ user.username }}</small>
                    </RouterLink>
                  </div>
                  <strong class="rank-count">{{ formatNumber(user.count) }}</strong>
                </div>
                <div class="rank-track">
                  <div
                    class="rank-fill rank-fill--user"
                    :style="{ width: `${toPercent(user.count)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="empty-state">
            <ui-icon name="users" />
            <p>No data available</p>
          </div>
        </div>
      </div>

      <!-- Recent Sensitive Activities -->
      <div class="chart-card chart-card--sensitive">
        <div class="chart-card-header chart-card-header--sensitive">
          <div class="chart-card-title">
            <ui-icon name="shield-alert" />
            <h2>Recent Sensitive Activities</h2>
          </div>
          <span v-if="summary.sensitive_logs.length" class="sensitive-badge-count">
            {{ summary.sensitive_logs.length }}
          </span>
        </div>
        <div class="chart-card-body chart-card-body--sensitive">
          <template v-if="summary.sensitive_logs.length">
            <div
              v-for="log in summary.sensitive_logs"
              :key="log.id"
              class="sensitive-row"
            >
              <div class="sensitive-row-left">
                <span class="sensitive-action-dot"></span>
                <div class="sensitive-info">
                  <strong class="sensitive-user">{{ log.user_full_name }}</strong>
                  <span class="sensitive-model">{{ log.model_name }}</span>
                </div>
              </div>
              <div class="sensitive-row-right">
                <span class="sensitive-tag">DELETE</span>
                <time class="sensitive-time">{{ formatRelativeTime(log.timestamp) }}</time>
              </div>
            </div>
          </template>
          <div v-else class="empty-state empty-state--success">
            <div class="success-icon-wrap">
              <ui-icon name="shield-check" />
            </div>
            <p>No sensitive activities</p>
            <span class="success-sub">All clear</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { fetchActivitySummary } from '@/services/activityLogsService'
import UiIcon from '@/components/ui/UiIcon.vue'

const summary = ref({
  total_logs: 0,
  today_logs: 0,
  week_logs: 0,
  month_logs: 0,
  actions_breakdown: [],
  modified_models: [],
  active_users: [],
  sensitive_logs: [],
})

const AVATAR_COLORS = [
  '#7c3aed', '#2563eb', '#0891b2', '#059669',
  '#d97706', '#dc2626', '#db2777', '#7c3aed',
]

function avatarColor(name) {
  let hash = 0
  for (const ch of String(name || '')) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/)
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
  return String(name || '?')[0].toUpperCase()
}

const todayPercent = computed(() => toPercent(summary.value.today_logs))
const weekPercent = computed(() => toPercent(summary.value.week_logs))
const monthPercent = computed(() => toPercent(summary.value.month_logs))

function formatNumber(value) {
  return Number(value || 0).toLocaleString()
}

function toPercent(value) {
  const total = Number(summary.value.total_logs || 0)
  if (!total) return 0
  return Math.max(2, Math.min(100, Math.round((Number(value || 0) / total) * 100)))
}

function formatRelativeTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000)
  const abs = Math.abs(diffSeconds)
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  if (abs < 60) return rtf.format(diffSeconds, 'second')
  const mins = Math.round(diffSeconds / 60)
  if (Math.abs(mins) < 60) return rtf.format(mins, 'minute')
  const hrs = Math.round(mins / 60)
  if (Math.abs(hrs) < 24) return rtf.format(hrs, 'hour')
  return rtf.format(Math.round(hrs / 24), 'day')
}

async function loadSummary() {
  const payload = await fetchActivitySummary()
  summary.value = {
    total_logs: Number(payload?.total_logs || 0),
    today_logs: Number(payload?.today_logs || 0),
    week_logs: Number(payload?.week_logs || 0),
    month_logs: Number(payload?.month_logs || 0),
    actions_breakdown: Array.isArray(payload?.actions_breakdown) ? payload.actions_breakdown : [],
    modified_models: Array.isArray(payload?.modified_models) ? payload.modified_models : [],
    active_users: Array.isArray(payload?.active_users) ? payload.active_users : [],
    sensitive_logs: Array.isArray(payload?.sensitive_logs) ? payload.sensitive_logs : [],
  }
}

onMounted(loadSummary)
</script>

<style scoped>
.summary-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-7) var(--space-5) var(--space-10);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  font-family: var(--font-sans);
}

/* ── Page Header ─────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}

.page-header-eyebrow {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--brand-navy-600);
  margin-bottom: var(--space-2);
}

.eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--status-success, #22c55e);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2); }
  50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.08); }
}

.page-header-title {
  font-size: clamp(1.35rem, 3vw, 1.875rem);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.page-header-desc {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 480px;
}

.btn-primary-action {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.625rem var(--space-4);
  background: var(--brand-navy-700);
  color: #fff;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-decoration: none;
  white-space: nowrap;
  transition: background var(--duration-fast), gap var(--duration-fast);
  flex-shrink: 0;
  align-self: flex-start;
  margin-top: var(--space-1);
}

.btn-primary-action:hover {
  background: var(--brand-navy-900);
  gap: var(--space-3);
}

.btn-arrow {
  font-size: 12px;
  opacity: 0.7;
}

/* ── KPI Grid ────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 500px) { .kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
  position: relative;
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: box-shadow var(--duration-fast), transform var(--duration-fast);
}

.kpi-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.kpi-card--today {
  border-color: var(--brand-navy-200);
  background: linear-gradient(145deg, color-mix(in srgb, var(--brand-navy-50, #eff6ff) 60%, white) 0%, var(--surface-base) 100%);
}

.kpi-card-inner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-4) var(--space-4);
}

.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.kpi-icon--total  { background: #f1f5f9; color: #64748b; }
.kpi-icon--today  { background: #dbeafe; color: #1d4ed8; }
.kpi-icon--week   { background: #d1fae5; color: #059669; }
.kpi-icon--month  { background: #fef3c7; color: #b45309; }

.kpi-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.kpi-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}

.kpi-card--today .kpi-label { color: var(--brand-navy-700); }

.kpi-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.kpi-card--today .kpi-value { color: var(--brand-navy-900); }

.kpi-note {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* Bottom progress indicator */
.kpi-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--brand-navy-700);
  border-radius: 0 2px 0 0;
  transition: width 1s var(--ease-out);
  opacity: 0.4;
}

.kpi-bar--full { width: 100%; opacity: 0.2; }
.kpi-card--today .kpi-bar { opacity: 0.6; background: #2563eb; }

/* ── Chart Grid ──────────────────────────────── */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
  align-items: start;
}

@media (max-width: 800px) { .chart-grid { grid-template-columns: 1fr; } }

/* ── Chart Card ──────────────────────────────── */
.chart-card {
  background: var(--surface-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.chart-card--sensitive {
  border-color: #fecaca;
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--surface-subtle);
}

.chart-card-header--sensitive {
  background: #fff5f5;
  border-color: #fecaca;
}

.chart-card-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.chart-card-title i {
  font-size: 14px;
  color: var(--text-secondary);
}

.chart-card-header--sensitive .chart-card-title i {
  color: #ef4444;
}

.chart-card-title h2 {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.chart-card-count {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: 99px;
  padding: 2px 8px;
}

.sensitive-badge-count {
  min-width: 22px;
  height: 22px;
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: var(--weight-bold);
  border-radius: 99px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.chart-card-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.chart-card-body--sensitive {
  padding: 0;
  gap: 0;
}

/* ── Progress Bars ───────────────────────────── */
.bar-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.bar-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.action-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.6875rem;
  font-weight: var(--weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.action-badge--create   { background: #dcfce7; color: #166534; }
.action-badge--delete   { background: #fee2e2; color: #991b1b; }
.action-badge--update   { background: #dbeafe; color: #1e40af; }
.action-badge--view     { background: #f3f4f6; color: #374151; }
.action-badge--download { background: #e0f2fe; color: #0369a1; }
.action-badge--import   { background: #fef3c7; color: #92400e; }

.bar-value {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin-left: auto;
}

.progress-track {
  position: relative;
  height: 10px;
  background: var(--surface-subtle);
  border-radius: 99px;
  overflow: visible;
  display: flex;
  align-items: center;
}

.progress-fill {
  height: 100%;
  border-radius: 99px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 4px;
  transition: width 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.progress-fill--create   { background: linear-gradient(90deg, #86efac, #16a34a); }
.progress-fill--delete   { background: linear-gradient(90deg, #fca5a5, #dc2626); }
.progress-fill--update   { background: linear-gradient(90deg, #93c5fd, #2563eb); }
.progress-fill--view     { background: linear-gradient(90deg, #d1d5db, #6b7280); }
.progress-fill--download { background: linear-gradient(90deg, #7dd3fc, #0284c7); }
.progress-fill--import   { background: linear-gradient(90deg, #fde68a, #d97706); }

.progress-pct {
  font-size: 0.5625rem;
  font-weight: var(--weight-bold);
  color: #fff;
  padding-right: 5px;
  white-space: nowrap;
}

.progress-pct-outside {
  font-size: 0.5625rem;
  font-weight: var(--weight-semibold);
  color: var(--text-muted);
  padding-left: var(--space-2);
  white-space: nowrap;
}

/* ── Rank Rows ───────────────────────────────── */
.rank-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: var(--weight-bold);
  background: var(--surface-subtle);
  color: var(--text-muted);
  flex-shrink: 0;
  border: 1px solid var(--border-subtle);
}

.rank-badge--top1 { background: #fef3c7; color: #92400e; border-color: #fde68a; }
.rank-badge--top2 { background: #f1f5f9; color: #475569; border-color: #cbd5e1; }
.rank-badge--top3 { background: #fff7ed; color: #9a3412; border-color: #fed7aa; }

.rank-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.rank-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.rank-link {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--brand-navy-700);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: text-decoration var(--duration-fast);
}

.rank-link:hover { text-decoration: underline; }

.rank-handle {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: var(--weight-normal);
  margin-left: var(--space-1);
}

.rank-count {
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  white-space: nowrap;
  flex-shrink: 0;
}

.rank-track {
  height: 4px;
  background: var(--surface-subtle);
  border-radius: 99px;
  overflow: hidden;
}

.rank-fill {
  height: 100%;
  background: var(--brand-navy-700);
  border-radius: 99px;
  transition: width 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  opacity: 0.6;
}

.rank-fill--user { background: #2563eb; opacity: 0.5; }

/* User identity in rank row */
.rank-row--user .rank-top { align-items: center; }

.user-identity {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  overflow: hidden;
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: var(--weight-bold);
  color: #fff;
  letter-spacing: 0.02em;
}

/* ── Sensitive Rows ──────────────────────────── */
.sensitive-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid #fef2f2;
  transition: background var(--duration-fast);
}

.sensitive-row:last-child { border-bottom: none; }
.sensitive-row:hover { background: #fff5f5; }

.sensitive-row-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  flex: 1;
  overflow: hidden;
}

.sensitive-action-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.sensitive-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.sensitive-user {
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sensitive-model {
  font-size: var(--text-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sensitive-row-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-1);
  flex-shrink: 0;
}

.sensitive-tag {
  font-size: 0.625rem;
  font-weight: var(--weight-bold);
  letter-spacing: 0.06em;
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 6px;
  border-radius: 4px;
}

.sensitive-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* ── Empty States ────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8) var(--space-4);
  gap: var(--space-2);
  color: var(--text-muted);
}

.empty-state i {
  font-size: 1.75rem;
  opacity: 0.4;
}

.empty-state p {
  margin: 0;
  font-size: var(--text-sm);
}

.empty-state--success {
  padding: var(--space-10) var(--space-4);
}

.success-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2);
}

.success-icon-wrap i {
  font-size: 1.5rem;
  color: #16a34a;
  opacity: 1;
}

.success-sub {
  font-size: var(--text-xs);
  color: #16a34a;
  font-weight: var(--weight-semibold);
}
</style>