"use strict";
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const QUARTERS = [
    { label: "Q1", range: "Jan - Mar" },
    { label: "Q2", range: "Apr - Jun" },
    { label: "Q3", range: "Jul - Sep" },
    { label: "Q4", range: "Oct - Dec" },
];
let expenses = [];
let currentFilter = "all";
let currentSort = { col: "total", dir: -1 };
function byId(id) {
    return document.getElementById(id);
}
function fmt(value) {
    return value > 0
        ? `P ${value.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
        : "-";
}
function sum(values) {
    return values.reduce((acc, value) => acc + value, 0);
}
function enrich() {
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
function quarterTotals(entry) {
    return {
        Q1: entry.q1t,
        Q2: entry.q2t,
        Q3: entry.q3t,
        Q4: entry.q4t,
    };
}
function renderExpenseCards() {
    const data = enrich();
    const grandTotal = data.reduce((total, entry) => total + entry.total, 0);
    const ytd = byId("ytd-total");
    if (ytd) {
        ytd.textContent = fmt(grandTotal);
    }
    const container = byId("summary-cards");
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
function renderExpenseTable() {
    var _a;
    const data = enrich();
    const grandTotal = data.reduce((total, entry) => total + entry.total, 0);
    const searchInput = byId("search-input");
    const search = ((_a = searchInput === null || searchInput === void 0 ? void 0 : searchInput.value) !== null && _a !== void 0 ? _a : "").toLowerCase();
    const tbody = byId("table-body");
    const tfoot = byId("table-foot");
    const noResults = byId("no-results");
    if (!tbody || !tfoot || !noResults) {
        return;
    }
    const numericSortMap = {
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
        const aValue = a[key];
        const bValue = b[key];
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
    document.querySelectorAll("thead th").forEach((headerCell) => {
        headerCell.classList.toggle("sorted", headerCell.dataset.col === currentSort.col);
    });
}
function renderExpenseAccordion() {
    const data = enrich();
    const accordion = byId("accordion");
    if (!accordion) {
        return;
    }
    accordion.innerHTML = "";
    QUARTERS.forEach((quarter, quarterIndex) => {
        const qKey = `q${quarterIndex + 1}`;
        const qKeyTotal = `q${quarterIndex + 1}t`;
        const quarterTotal = data.reduce((total, entry) => total + entry[qKeyTotal], 0);
        const isFirstQuarter = quarterIndex === 0;
        const item = document.createElement("div");
        item.className = `acc-item${isFirstQuarter ? " open" : ""}`;
        const badgeHtml = isFirstQuarter
            ? `<span class="acc-badge active">Active</span>`
            : `<span class="acc-badge">${quarterTotal > 0 ? "Has Data" : "No Data"}</span>`;
        const monthsHtml = [0, 1, 2]
            .map((monthOffset) => {
            var _a;
            const monthIndex = quarterIndex * 3 + monthOffset;
            const monthName = (_a = MONTHS[monthIndex]) !== null && _a !== void 0 ? _a : "";
            const entries = data.filter((entry) => { var _a; return ((_a = entry[qKey][monthOffset]) !== null && _a !== void 0 ? _a : 0) > 0; });
            const monthTotal = entries.reduce((total, entry) => { var _a; return total + ((_a = entry[qKey][monthOffset]) !== null && _a !== void 0 ? _a : 0); }, 0);
            const hasData = monthTotal > 0;
            return `
          <div class="month-col">
            <div class="month-title ${hasData ? "has-data" : ""}">
              <span>${monthName}</span>
              <span>${hasData ? fmt(monthTotal) : "-"}</span>
            </div>
            ${hasData
                ? entries
                    .map((entry) => {
                    var _a;
                    return `
                <div class="month-entry">
                  <span class="entry-label">
                    <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:${entry.color};flex-shrink:0"></span>
                    ${entry.name}
                  </span>
                  <span class="entry-val has-val">${fmt((_a = entry[qKey][monthOffset]) !== null && _a !== void 0 ? _a : 0)}</span>
                </div>`;
                })
                    .join("")
                : `<div class="month-entry">
                    <span class="entry-label">No expenses</span>
                    <span class="entry-val no-val">-</span>
                  </div>`}
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
        const header = item.querySelector(".acc-header");
        if (header) {
            header.addEventListener("click", () => {
                item.classList.toggle("open");
            });
        }
        accordion.appendChild(item);
    });
}
function initExpensesReport(expenseData) {
    expenses = expenseData !== null && expenseData !== void 0 ? expenseData : [];
    currentFilter = "all";
    currentSort = { col: "total", dir: -1 };
    document.querySelectorAll(".filter-btn").forEach((button) => {
        const replacement = button.cloneNode(true);
        const parent = button.parentNode;
        if (parent) {
            parent.replaceChild(replacement, button);
        }
    });
    document.querySelectorAll(".filter-btn").forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn").forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            const selectedQuarter = button.dataset.q;
            if (selectedQuarter === "Q1" || selectedQuarter === "Q2" || selectedQuarter === "Q3" || selectedQuarter === "Q4") {
                currentFilter = selectedQuarter;
            }
            else {
                currentFilter = "all";
            }
            renderExpenseTable();
        });
    });
    const searchInput = byId("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", renderExpenseTable);
    }
    document.querySelectorAll("thead th[data-col]").forEach((headerCell) => {
        headerCell.addEventListener("click", () => {
            const column = headerCell.dataset.col;
            if (!column || column === "q1" || column === "q2" || column === "q3" || column === "q4") {
                return;
            }
            if (column === "name" || column === "total" || column === "pct") {
                if (currentSort.col === column) {
                    currentSort.dir = currentSort.dir === 1 ? -1 : 1;
                }
                else {
                    currentSort = { col: column, dir: -1 };
                }
                renderExpenseTable();
            }
        });
    });
    const exportButton = byId("btn-export");
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
function initializeExpensesIfReady() {
    if (Array.isArray(EXPENSES_DATA)) {
        initExpensesReport(EXPENSES_DATA);
        return;
    }
    console.error("Expense data not found. Make sure EXPENSES_DATA is available in the template.");
}
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeExpensesIfReady);
}
else {
    initializeExpensesIfReady();
}
//# sourceMappingURL=expenses-report-render.js.map