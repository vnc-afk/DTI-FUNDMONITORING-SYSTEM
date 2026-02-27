# DTI Fund Monitoring System - Project Organization Guide

## Overview
The project has been reorganized by functionality and purpose for better maintainability and scalability.

---

## 📁 Project Structure

### dashboard_app/
```
dashboard_app/
├── models/                    # Data models organized by entity
│   ├── __init__.py
│   ├── staff.py             # Staff model
│   ├── supplier.py          # Supplier model
│   └── funding.py           # FundSource, BudgetBreakdown, BankStatement models
│
├── views/                     # View functions organized by feature
│   ├── __init__.py
│   ├── dashboard.py         # Dashboard views
│   ├── staff.py             # Staff CRUD operations
│   ├── supplier.py          # Supplier CRUD operations
│   ├── funding.py           # Fund sources & bank statements CRUD
│   └── reports.py           # Report generation & export views
│
├── forms/                     # Form classes organized by entity
│   ├── __init__.py
│   ├── staff.py             # StaffForm
│   ├── supplier.py          # SupplierForm
│   └── funding.py           # FundSourceForm, BankStatementForm
│
├── templates/                 # HTML templates organized by feature
│   ├── base.html            # Base template for all pages
│   ├── dashboard.html       # Dashboard home page
│   ├── staff/               # Staff management templates
│   │   ├── list.html        # Staff list view
│   │   ├── form.html        # Staff add/edit form
│   │   └── confirm_delete.html
│   │
│   ├── supplier/            # Supplier management templates
│   │   ├── list.html        # Supplier list view
│   │   ├── form.html        # Supplier add/edit form
│   │   └── confirm_delete.html
│   │
│   ├── funding/             # Fund & bank statement templates
│   │   ├── fund_sources.html
│   │   ├── fund_source_form.html
│   │   ├── fund_source_confirm_delete.html
│   │   ├── bank_statement.html
│   │   ├── bank_statement_form.html
│   │   └── bank_statement_confirm_delete.html
│   │
│   └── reports/             # Report templates
│       ├── allocations/     # Allocation/disbursement reports
│       │   ├── disbursement_table.html
│       │   ├── downloads_table.html
│       │   ├── fund_disbursement_table.html
│       │   ├── fund_downloads_table.html
│       │   ├── nc_district1_table.html
│       │   ├── nc_district2_table.html
│       │   ├── nc_district3_table.html
│       │   └── tin.html
│       ├── expenses_report.html
│       ├── fund_report.html
│       ├── mooe_report.html
│       └── negosyo_center_report.html
│
├── static/dashboard_app/      # Static assets organized by type and purpose
│   ├── css/
│   │   ├── layouts/         # Page structure & layout styles
│   │   │   ├── base.css
│   │   │   └── sidebar.css
│   │   │
│   │   ├── components/      # Reusable component styles
│   │   │   ├── form.css     # Form styles
│   │   │   └── table.css    # Table styles
│   │   │
│   │   └── pages/           # Page-specific styles
│   │       └── report.css   # Report pages styles
│   │
│   └── js/
│       └── modules/         # JavaScript modules/functionality
│           ├── app.js       # Main app functionality
│           ├── expenses.js  # Expense report logic
│           └── table.js     # Table interactions
│
├── migrations/                # Database migration files
├── admin.py                  # Django admin configuration
├── apps.py                   # App configuration
└── tests.py                  # Test files
```

---

## 🗂️ File Mapping & Organization Guide

### OLD → NEW Structure

#### Models
| Old File | New Location |
|----------|-------------|
| `models.py` (Staff) | `models/staff.py` |
| `models.py` (Supplier) | `models/supplier.py` |
| `models.py` (FundSource, BudgetBreakdown, BankStatement) | `models/funding.py` |

#### Forms
| Old File | New Location |
|----------|-------------|
| `forms.py` (StaffForm) | `forms/staff.py` |
| `forms.py` (SupplierForm) | `forms/supplier.py` |
| `forms.py` (FundSourceForm, BankStatementForm) | `forms/funding.py` |

#### Views
| Old File | New Location |
|----------|-------------|
| `views.py` (staff_list, staff_add, staff_edit, staff_delete) | `views/staff.py` |
| `views.py` (supplier_list, supplier_add, supplier_edit, supplier_delete) | `views/supplier.py` |
| `views.py` (fund_sources_view, fund_source_create, fund_source_update, fund_source_delete, bank_statement_*) | `views/funding.py` |
| `views.py` (expense_report, mooe_report, nc_report, fund_report, download_mooe) | `views/reports.py` |
| `views.py` (dashboard) | `views/dashboard.py` |

#### Templates
| Old File | New Location |
|----------|-------------|
| `templates/staff_list.html` | `templates/staff/list.html` |
| `templates/staff_form.html` | `templates/staff/form.html` |
| `templates/staff_confirm_delete.html` | `templates/staff/confirm_delete.html` |
| `templates/supplier_list.html` | `templates/supplier/list.html` |
| `templates/supplier_form.html` | `templates/supplier/form.html` |
| `templates/supplier_confirm_delete.html` | `templates/supplier/confirm_delete.html` |
| `templates/fund_sources.html` | `templates/funding/fund_sources.html` |
| `templates/fund_source_form.html` | `templates/funding/fund_source_form.html` |
| `templates/bank_statement.html` | `templates/funding/bank_statement.html` |
| `templates/bank_statement_form.html` | `templates/funding/bank_statement_form.html` |
| `templates/expenses_report.html` | `templates/reports/expenses_report.html` |
| `templates/mooe_report.html` | `templates/reports/mooe_report.html` |
| `templates/negosyo_center_report.html` | `templates/reports/negosyo_center_report.html` |
| `templates/fund_report.html` | `templates/reports/fund_report.html` |
| `templates/disbursement_table.html` | `templates/reports/allocations/disbursement_table.html` |
| `templates/downloads_table.html` | `templates/reports/allocations/downloads_table.html` |
| `templates/fund_disbursement_table.html` | `templates/reports/allocations/fund_disbursement_table.html` |
| `templates/fund_downloads_table.html` | `templates/reports/allocations/fund_downloads_table.html` |
| `templates/nc_district*.html` | `templates/reports/allocations/` |
| `templates/tin.html` | `templates/reports/allocations/tin.html` |
| `templates/base.html` | `templates/base.html` (no change) |
| `templates/dashboard.html` | `templates/dashboard.html` (no change) |

#### Static Files
| Old File | New Location |
|----------|-------------|
| `static/dashboard_app/css/base.css` | `static/dashboard_app/css/layouts/base.css` |
| `static/dashboard_app/css/sidebar.css` | `static/dashboard_app/css/layouts/sidebar.css` |
| `static/dashboard_app/css/form.css` | `static/dashboard_app/css/components/form.css` |
| `static/dashboard_app/css/table.css` | `static/dashboard_app/css/components/table.css` |
| `static/dashboard_app/css/report.css` | `static/dashboard_app/css/pages/report.css` |
| `static/dashboard_app/js/app.js` | `static/dashboard_app/js/modules/app.js` |
| `static/dashboard_app/js/expenses.js` | `static/dashboard_app/js/modules/expenses.js` |
| `static/dashboard_app/js/table.js` | `static/dashboard_app/js/modules/table.js` |

---

## 📋 Benefits of This Organization

1. **Scalability**: Easy to add new apps, models, views without making files cluttered
2. **Maintainability**: Related code is grouped together by feature/entity
3. **Modularity**: Each module has a single responsibility
4. **Clarity**: Template/static file organization mirrors feature structure
5. **Navigation**: Developers can quickly find relevant code
6. **Testing**: Easier to write and organize tests by feature

---

## 🔧 Implementation Notes

### Imports Update Required
When updating code, remember to update imports:

**Old syntax:**
```python
from dashboard_app.models import Staff, Supplier, FundSource, BudgetBreakdown, BankStatement
from dashboard_app.forms import StaffForm, SupplierForm, FundSourceForm, BankStatementForm
from dashboard_app.views import staff_list, supplier_list, ...
```

**New syntax:**
```python
from dashboard_app.models import Staff, Supplier, FundSource, BudgetBreakdown, BankStatement
from dashboard_app.forms import StaffForm, SupplierForm, FundSourceForm, BankStatementForm
from dashboard_app.views import staff_list, supplier_list, ...  # Still works via __init__.py
```

### Template Loader Path
Django's template loader will find templates based on the APP_DIRS setting. When loading templates:
- `render(request, 'staff/list.html', context)` - Will find `dashboard_app/templates/staff/list.html`
- `render(request, 'reports/expenses_report.html', context)` - Will find `dashboard_app/templates/reports/expenses_report.html`

---

## 📝 Next Steps

1. **Move template files** to their new locations
2. **Move static files** to their organized folders
3. **Update URL patterns** in `urls.py` if needed
4. **Update template includes** in base.html for CSS/JS paths
5. **Test the application** to ensure all imports and template references work
6. **Update any admin.py** references if needed

