type QuarterKey = "q1" | "q2" | "q3" | "q4";
type QuarterFilter = "Q1" | "Q2" | "Q3" | "Q4";
type Filter = "all" | QuarterFilter;
type SortCol = "name" | "total" | "pct" | QuarterKey;

interface ExpenseEntry {
  name: string;
  color: string;
  q1: number[];
  q2: number[];
  q3: number[];
  q4: number[];
}

interface EnrichedExpense extends ExpenseEntry {
  q1t: number;
  q2t: number;
  q3t: number;
  q4t: number;
  total: number;
}

interface QuarterInfo {
  label: QuarterFilter;
  range: string;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] as const;

const QUARTERS: QuarterInfo[] = [
  { label: "Q1", range: "Jan - Mar" },
  { label: "Q2", range: "Apr - Jun" },
  { label: "Q3", range: "Jul - Sep" },
  { label: "Q4", range: "Oct - Dec" },
];

let expenses: ExpenseEntry[] = [];
let currentFilter: Filter = "all";
let currentSort: { col: SortCol; dir: 1 | -1 } = { col: "total", dir: -1 };

function byId<T extends HTMLElement>(id: string): T | null {
  return document.getElementById(id) as T | null;
}

function fmt(value: number): string {
  return value > 0
    ? `₱ ${value.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : "-";
}

function sum(values: number[]): number {
  return values.reduce((acc, value) => acc + value, 0);
}

function enrich(): EnrichedExpense[] {
  return expenses.map((entry) => {
    const q1t = sum(entry.q1);
    const q2t = sum(entry.q2);
    const q3t = sum(entry.q3);
    const q4t = sum(entry.q4);

    return {
      ...entry,
      q1t,
      q2t,
      q3t,
      q4t,
      total: q1t + q2t + q3t + q4t,
    };
  });
}

function quarterTotals(entry: EnrichedExpense): Record<QuarterFilter, number> {
  return {
    Q1: entry.q1t,
    Q2: entry.q2t,
    Q3: entry.q3t,
    Q4: entry.q4t,
  };
}

function renderExpenseCards(): void {
  const data = enrich();
  const grandTotal = data.reduce((total, entry) => total + entry.total, 0);

  const ytd = byId<HTMLElement>("ytd-total");
  if (ytd) {
    ytd.textContent = fmt(grandTotal);
  }

  const container = byId<HTMLElement>("summary-cards");
  if (!container) {
    return;
  }

  container.innerHTML = "";

  data
    .filter((entry) => entry.total > 0)
    .forEach((entry, index) => {
      const pct = grandTotal > 0 ? ((entry.total / grandTotal) * 100).toFixed(1) : "0.0";
      const card = document.createElement("div");
      card.className = "scard";
      card.style.animationDelay = `${index * 0.025}s`;
      card.style.borderLeft = `2px solid ${entry.color}`;
      card.innerHTML = `
        <div class="scard-label">${entry.name}</div>
        <div class="scard-amount" style="color:${entry.color}">${fmt(entry.total)}</div>
        <div class="scard-pct">${pct}% of total</div>
        <div class="scard-bar"><div class="scard-bar-fill" style="width:${pct}%;background:${entry.color}"></div></div>
      `;
      container.appendChild(card);
    });
}

function renderExpenseTable(): void {
  const data = enrich();
  const grandTotal = data.reduce((total, entry) => total + entry.total, 0);

  const searchInput = byId<HTMLInputElement>("search-input");
  const search = (searchInput?.value ?? "").toLowerCase();

  const tbody = byId<HTMLElement>("table-body");
  const tfoot = byId<HTMLElement>("table-foot");
  const noResults = byId<HTMLElement>("no-results");

  if (!tbody || !tfoot || !noResults) {
    return;
  }

  const numericSortMap: Record<Exclude<SortCol, "name">, keyof EnrichedExpense> = {
    total: "total",
    pct: "total",
    q1: "q1t",
    q2: "q2t",
    q3: "q3t",
    q4: "q4t",
  };

  const sorted = [...data].sort((a, b) => {
    if (currentSort.col === "name") {
      return currentSort.dir * a.name.localeCompare(b.name);
    }

    const key = numericSortMap[currentSort.col];
    const aValue = a[key] as number;
    const bValue = b[key] as number;
    return currentSort.dir * (aValue - bValue);
  });

  tbody.innerHTML = "";
  let visibleCount = 0;

  sorted.forEach((entry) => {
    const pct = grandTotal > 0 ? ((entry.total / grandTotal) * 100).toFixed(2) : "0.00";
    const qMap = quarterTotals(entry);
    const matchesSearch = entry.name.toLowerCase().includes(search);
    const matchesQuarter = currentFilter === "all" || qMap[currentFilter] > 0;

    if (!matchesSearch || !matchesQuarter) {
      return;
    }

    visibleCount += 1;
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><span class="cat-dot" style="background:${entry.color}"></span>${entry.name}</td>
      <td class="amount ${entry.total > 0 ? "pos" : "empty"}">${fmt(entry.total)}</td>
      <td><span class="pct-badge">${entry.total > 0 ? `${pct}%` : "-"}</span></td>
      <td class="q-cell ${entry.q1t > 0 ? "active" : "inactive"}">${fmt(entry.q1t)}</td>
      <td class="q-cell ${entry.q2t > 0 ? "active" : "inactive"}">${fmt(entry.q2t)}</td>
      <td class="q-cell ${entry.q3t > 0 ? "active" : "inactive"}">${fmt(entry.q3t)}</td>
      <td class="q-cell ${entry.q4t > 0 ? "active" : "inactive"}">${fmt(entry.q4t)}</td>
    `;
    tbody.appendChild(row);
  });

  noResults.style.display = visibleCount === 0 ? "block" : "none";

  const visibleRows = sorted.filter((entry) => {
    const qMap = quarterTotals(entry);
    return entry.name.toLowerCase().includes(search) && (currentFilter === "all" || qMap[currentFilter] > 0);
  });

  const subtotalTotal = visibleRows.reduce((total, entry) => total + entry.total, 0);
  const subtotalByQuarter = [
    visibleRows.reduce((total, entry) => total + entry.q1t, 0),
    visibleRows.reduce((total, entry) => total + entry.q2t, 0),
    visibleRows.reduce((total, entry) => total + entry.q3t, 0),
    visibleRows.reduce((total, entry) => total + entry.q4t, 0),
  ];

  tfoot.innerHTML = `<tr>
    <td>Subtotal (${visibleCount} shown)</td>
    <td>${fmt(subtotalTotal)}</td>
    <td></td>
    ${subtotalByQuarter.map((value) => `<td>${fmt(value)}</td>`).join("")}
  </tr>`;

  document.querySelectorAll<HTMLTableCellElement>("thead th").forEach((headerCell) => {
    headerCell.classList.toggle("sorted", headerCell.dataset.col === currentSort.col);
  });
}

function renderExpenseAccordion(): void {
  const data = enrich();
  const accordion = byId<HTMLElement>("accordion");
  if (!accordion) {
    return;
  }

  accordion.innerHTML = "";

  QUARTERS.forEach((quarter, quarterIndex) => {
    const qKey = (`q${quarterIndex + 1}` as QuarterKey);
    const qKeyTotal = (`q${quarterIndex + 1}t` as keyof EnrichedExpense);
    const quarterTotal = data.reduce((total, entry) => total + (entry[qKeyTotal] as number), 0);
    const isFirstQuarter = quarterIndex === 0;

    const item = document.createElement("div");
    item.className = `acc-item${isFirstQuarter ? " open" : ""}`;

    const badgeHtml = isFirstQuarter
      ? `<span class="acc-badge active">Active</span>`
      : `<span class="acc-badge">${quarterTotal > 0 ? "Has Data" : "No Data"}</span>`;

    const monthsHtml = [0, 1, 2]
      .map((monthOffset) => {
        const monthIndex = quarterIndex * 3 + monthOffset;
        const monthName = MONTHS[monthIndex] ?? "";

        const entries = data.filter((entry) => (entry[qKey][monthOffset] ?? 0) > 0);
        const monthTotal = entries.reduce((total, entry) => total + (entry[qKey][monthOffset] ?? 0), 0);
        const hasData = monthTotal > 0;

        return `
          <div class="month-col">
            <div class="month-title ${hasData ? "has-data" : ""}">
              <span>${monthName}</span>
              <span>${hasData ? fmt(monthTotal) : "-"}</span>
            </div>
            ${
              hasData
                ? entries
                    .map(
                      (entry) => `
                <div class="month-entry">
                  <span class="entry-label">
                    <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:${entry.color};flex-shrink:0"></span>
                    ${entry.name}
                  </span>
                  <span class="entry-val has-val">${fmt(entry[qKey][monthOffset] ?? 0)}</span>
                </div>`
                    )
                    .join("")
                : `<div class="month-entry">
                    <span class="entry-label">No expenses</span>
                    <span class="entry-val no-val">-</span>
                  </div>`
            }
          </div>
        `;
      })
      .join("");

    item.innerHTML = `
      <div class="acc-header">
        <div class="acc-header-left">
          <div class="acc-q-label">${quarter.label}</div>
          <div class="acc-q-range">${quarter.range}</div>
        </div>
        <div class="acc-header-right">
          ${badgeHtml}
          <div class="acc-total ${quarterTotal === 0 ? "empty" : ""}">${quarterTotal > 0 ? fmt(quarterTotal) : "No expenses"}</div>
          <div class="acc-chevron">▼</div>
        </div>
      </div>
      <div class="acc-body">
        <div class="months-row">${monthsHtml}</div>
      </div>
    `;

    const header = item.querySelector<HTMLElement>(".acc-header");
    if (header) {
      header.addEventListener("click", () => {
        item.classList.toggle("open");
      });
    }

    accordion.appendChild(item);
  });
}

function initExpensesReport(expenseData: ExpenseEntry[] | undefined): void {
  expenses = expenseData ?? [];
  currentFilter = "all";
  currentSort = { col: "total", dir: -1 };

  document.querySelectorAll<HTMLElement>(".filter-btn").forEach((button) => {
    const replacement = button.cloneNode(true);
    const parent = button.parentNode;
    if (parent) {
      parent.replaceChild(replacement, button);
    }
  });

  document.querySelectorAll<HTMLElement>(".filter-btn").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll<HTMLElement>(".filter-btn").forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      const selectedQuarter = button.dataset.q;
      if (selectedQuarter === "Q1" || selectedQuarter === "Q2" || selectedQuarter === "Q3" || selectedQuarter === "Q4") {
        currentFilter = selectedQuarter;
      } else {
        currentFilter = "all";
      }

      renderExpenseTable();
    });
  });

  const searchInput = byId<HTMLInputElement>("search-input");
  if (searchInput) {
    searchInput.addEventListener("input", renderExpenseTable);
  }

  document.querySelectorAll<HTMLTableCellElement>("thead th[data-col]").forEach((headerCell) => {
    headerCell.addEventListener("click", () => {
      const column = headerCell.dataset.col;
      if (!column || column === "q1" || column === "q2" || column === "q3" || column === "q4") {
        return;
      }

      if (column === "name" || column === "total" || column === "pct") {
        if (currentSort.col === column) {
          currentSort.dir = currentSort.dir === 1 ? -1 : 1;
        } else {
          currentSort = { col: column, dir: -1 };
        }
        renderExpenseTable();
      }
    });
  });

  const exportButton = byId<HTMLElement>("btn-export");
  if (exportButton) {
    exportButton.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (typeof exportExpensesReportAll === "function") {
        exportExpensesReportAll();
      }
    });
  }

  renderExpenseCards();
  renderExpenseTable();
  renderExpenseAccordion();
}

function initializeExpensesIfReady(): void {
  if (Array.isArray(EXPENSES_DATA)) {
    initExpensesReport(EXPENSES_DATA);
    return;
  }

  console.error("Expense data not found. Make sure EXPENSES_DATA is available in the template.");
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeExpensesIfReady);
} else {
  initializeExpensesIfReady();
}
