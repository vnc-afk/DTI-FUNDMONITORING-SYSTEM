// ─── EXPENSE DATA ────────────────────────────────────────────────────────────
// Each entry: name, color (hex), and monthly arrays:
//   q1: [Jan, Feb, Mar]   q2: [Apr, May, Jun]
//   q3: [Jul, Aug, Sep]   q4: [Oct, Nov, Dec]
// Add or remove as many objects as needed — everything renders automatically.

const EXPENSES = [
  { name: "Traveling Expenses - Local",  color: "#c8f065", q1: [58408.31, 0, 0],              q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Training Expenses",           color: "#f0c865", q1: [33330.12, 0, 0],              q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Office Supplies",             color: "#65c8f0", q1: [12400.00, 5200.00, 0],        q2: [8900.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Representation Expenses",     color: "#f065c8", q1: [9800.00, 0, 0],               q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Communication Expenses",      color: "#c865f0", q1: [4500.00, 4500.00, 4500.00],   q2: [4500.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Fuel Expenses",               color: "#65f0c8", q1: [7200.00, 6800.00, 0],         q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Postage & Delivery",          color: "#f0e865", q1: [1200.00, 0, 0],               q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Printing & Reproduction",     color: "#65f0f0", q1: [3400.00, 2100.00, 0],         q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Subscription Expenses",       color: "#a0c8ff", q1: [8500.00, 8500.00, 8500.00],   q2: [8500.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Rent/Lease Expenses",         color: "#ffaac8", q1: [45000.00, 45000.00, 45000.00],q2: [45000.00,0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Electricity",                 color: "#c8ffc8", q1: [18200.00, 17400.00, 19100.00],q2: [18600.00,0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Water",                       color: "#c8e0ff", q1: [3200.00, 3100.00, 3400.00],   q2: [3300.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Internet & Telecom",          color: "#ffd4a0", q1: [5200.00, 5200.00, 5200.00],   q2: [5200.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Insurance",                   color: "#d4a0ff", q1: [22000.00, 0, 0],              q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Janitorial Supplies",         color: "#a0ffd4", q1: [4800.00, 4200.00, 0],         q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Security Services",           color: "#ffc8a0", q1: [15000.00, 15000.00, 15000.00],q2: [15000.00,0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Advertising & Promotions",    color: "#a0c8c8", q1: [12000.00, 0, 0],              q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Professional Fees",           color: "#c8a0ff", q1: [30000.00, 0, 0],              q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Depreciation - Equipment",    color: "#ffd4d4", q1: [8750.00, 8750.00, 8750.00],   q2: [8750.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Depreciation - Furniture",    color: "#d4ffd4", q1: [2100.00, 2100.00, 2100.00],   q2: [2100.00, 0, 0], q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Repairs & Maintenance",       color: "#f09065", q1: [0, 0, 0],                     q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Medical & Dental",            color: "#ffa0a0", q1: [0, 0, 0],                     q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
  { name: "Miscellaneous Expenses",      color: "#d4d4ff", q1: [5500.00, 3200.00, 0],         q2: [0, 0, 0],       q3: [0, 0, 0], q4: [0, 0, 0] },
];

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