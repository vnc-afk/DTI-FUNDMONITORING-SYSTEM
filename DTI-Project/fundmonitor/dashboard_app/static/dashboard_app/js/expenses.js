// ─── EXPENSE DATA ────────────────────────────────────────────────────────────
// Each entry: name, color (hex), and monthly arrays:
//   q1: [Jan, Feb, Mar]   q2: [Apr, May, Jun]
//   q3: [Jul, Aug, Sep]   q4: [Oct, Nov, Dec]
// Add or remove as many objects as needed — everything renders automatically.

const EXPENSES = [];

// ─── CONSTANTS ───────────────────────────────────────────────────────────────
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const QUARTERS = [
  { label: "Q1", range: "Jan – Mar" },
  { label: "Q2", range: "Apr – Jun" },
  { label: "Q3", range: "Jul – Sep" },
  { label: "Q4", range: "Oct – Dec" },
];

// ─── STATE ───────────────────────────────────────────────────────────────────
let currentFilter = 'all';
let currentSort = { col: 'total', dir: -1 };

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const fmt = n => n > 0
  ? `₱ ${n.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  : '—';

function enrich() {
  return EXPENSES.map(e => {
    const q1t = e.q1.reduce((a, b) => a + b, 0);
    const q2t = e.q2.reduce((a, b) => a + b, 0);
    const q3t = e.q3.reduce((a, b) => a + b, 0);
    const q4t = e.q4.reduce((a, b) => a + b, 0);
    return { ...e, q1t, q2t, q3t, q4t, total: q1t + q2t + q3t + q4t };
  });
}

// ─── SUMMARY CARDS ───────────────────────────────────────────────────────────
function renderExpenseCards() {
  const data = enrich();
  const gt = data.reduce((s, e) => s + e.total, 0);
  document.getElementById('ytd-total').textContent = fmt(gt);

  const container = document.getElementById('summary-cards');
  data.filter(e => e.total > 0).forEach((e, i) => {
    const pct = gt > 0 ? ((e.total / gt) * 100).toFixed(1) : 0;
    const d = document.createElement('div');
    d.className = 'scard';
    d.style.animationDelay = `${i * 0.025}s`;
    d.style.borderLeft = `2px solid ${e.color}`;
    d.innerHTML = `
      <div class="scard-label">${e.name}</div>
      <div class="scard-amount" style="color:${e.color}">${fmt(e.total)}</div>
      <div class="scard-pct">${pct}% of total</div>
      <div class="scard-bar"><div class="scard-bar-fill" style="width:${pct}%;background:${e.color}"></div></div>
    `;
    container.appendChild(d);
  });
}

// ─── MAIN TABLE ──────────────────────────────────────────────────────────────
function renderExpenseTable() {
  const data = enrich();
  const gt = data.reduce((s, e) => s + e.total, 0);
  const search = document.getElementById('search-input').value.toLowerCase();
  const tbody = document.getElementById('table-body');
  const tfoot = document.getElementById('table-foot');

  // Sort
  const sorted = [...data].sort((a, b) => {
    if (currentSort.col === 'name') return currentSort.dir * a.name.localeCompare(b.name);
    const map = { total: 'total', pct: 'total', q1: 'q1t', q2: 'q2t', q3: 'q3t', q4: 'q4t' };
    return currentSort.dir * (a[map[currentSort.col]] - b[map[currentSort.col]]);
  });

  tbody.innerHTML = '';
  let visCount = 0;

  sorted.forEach(e => {
    const pct = gt > 0 ? ((e.total / gt) * 100).toFixed(2) : '0.00';
    const qMap = { Q1: e.q1t, Q2: e.q2t, Q3: e.q3t, Q4: e.q4t };
    const matchSearch = e.name.toLowerCase().includes(search);
    const matchQ = currentFilter === 'all' || qMap[currentFilter] > 0;

    if (!matchSearch || !matchQ) {
      return;
    }

    visCount++;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><span class="cat-dot" style="background:${e.color}"></span>${e.name}</td>
      <td class="amount ${e.total > 0 ? 'pos' : 'empty'}">${fmt(e.total)}</td>
      <td><span class="pct-badge">${e.total > 0 ? pct + '%' : '—'}</span></td>
      <td class="q-cell ${e.q1t > 0 ? 'active' : 'inactive'}">${fmt(e.q1t)}</td>
      <td class="q-cell ${e.q2t > 0 ? 'active' : 'inactive'}">${fmt(e.q2t)}</td>
      <td class="q-cell ${e.q3t > 0 ? 'active' : 'inactive'}">${fmt(e.q3t)}</td>
      <td class="q-cell ${e.q4t > 0 ? 'active' : 'inactive'}">${fmt(e.q4t)}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('no-results').style.display = visCount === 0 ? 'block' : 'none';

  // Footer subtotals
  const vis = sorted.filter(e => {
    const qMap = { Q1: e.q1t, Q2: e.q2t, Q3: e.q3t, Q4: e.q4t };
    return e.name.toLowerCase().includes(search) && (currentFilter === 'all' || qMap[currentFilter] > 0);
  });
  const sTotal = vis.reduce((s, e) => s + e.total, 0);
  const sQ = [1, 2, 3, 4].map(q => vis.reduce((s, e) => s + e[`q${q}t`], 0));

  tfoot.innerHTML = `<tr>
    <td>Subtotal (${visCount} shown)</td>
    <td>${fmt(sTotal)}</td>
    <td></td>
    ${sQ.map(v => `<td>${fmt(v)}</td>`).join('')}
  </tr>`;

  // Highlight sorted column header
  document.querySelectorAll('thead th').forEach(th => {
    th.classList.toggle('sorted', th.dataset.col === currentSort.col);
  });
}

// ─── ACCORDION ───────────────────────────────────────────────────────────────
function renderExpenseAccordion() {
  const data = enrich();
  const acc = document.getElementById('accordion');

  QUARTERS.forEach((q, qi) => {
    const qKey = `q${qi + 1}`;
    const qTotal = data.reduce((s, e) => s + e[`${qKey}t`], 0);
    const isQ1 = qi === 0;

    const item = document.createElement('div');
    item.className = 'acc-item' + (isQ1 ? ' open' : '');

    const badge = isQ1
      ? `<span class="acc-badge active">Active</span>`
      : `<span class="acc-badge">${qTotal > 0 ? 'Has Data' : 'No Data'}</span>`;

    const monthsHtml = [0, 1, 2].map(mi => {
      const globalMi = qi * 3 + mi;
      const monthName = MONTHS[globalMi];
      const entries = data.filter(e => e[qKey][mi] > 0);
      const monthTotal = entries.reduce((s, e) => s + e[qKey][mi], 0);
      const hasData = monthTotal > 0;

      return `
        <div class="month-col">
          <div class="month-title ${hasData ? 'has-data' : ''}">
            <span>${monthName}</span>
            <span>${hasData ? fmt(monthTotal) : '—'}</span>
          </div>
          ${hasData
            ? entries.map(e => `
                <div class="month-entry">
                  <span class="entry-label">
                    <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:${e.color};flex-shrink:0"></span>
                    ${e.name}
                  </span>
                  <span class="entry-val has-val">${fmt(e[qKey][mi])}</span>
                </div>`).join('')
            : `<div class="month-entry">
                <span class="entry-label">No expenses</span>
                <span class="entry-val no-val">—</span>
               </div>`
          }
        </div>
      `;
    }).join('');

    item.innerHTML = `
      <div class="acc-header">
        <div class="acc-header-left">
          <div class="acc-q-label">${q.label}</div>
          <div class="acc-q-range">${q.range}</div>
        </div>
        <div class="acc-header-right">
          ${badge}
          <div class="acc-total ${qTotal === 0 ? 'empty' : ''}">${qTotal > 0 ? fmt(qTotal) : 'No expenses'}</div>
          <div class="acc-chevron">▼</div>
        </div>
      </div>
      <div class="acc-body">
        <div class="months-row">${monthsHtml}</div>
      </div>
    `;

    item.querySelector('.acc-header').addEventListener('click', () => {
      item.classList.toggle('open');
    });

    acc.appendChild(item);
  });
}

// ─── EVENT LISTENERS ─────────────────────────────────────────────────────────
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.q;
    renderExpenseTable();
  });
});

document.getElementById('search-input').addEventListener('input', renderExpenseTable);

document.querySelectorAll('thead th[data-col]').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.col;
    if (['q1', 'q2', 'q3', 'q4'].includes(col)) return;
    currentSort.col === col
      ? (currentSort.dir *= -1)
      : (currentSort.col = col, currentSort.dir = -1);
    renderExpenseTable();
  });
});

// ─── INIT ─────────────────────────────────────────────────────────────────────
renderExpenseCards();
renderExpenseTable();
renderExpenseAccordion();