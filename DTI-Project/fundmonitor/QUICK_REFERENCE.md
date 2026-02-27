# Quick Start Guide - Project Navigation

## 🎯 Find What You Need

### Finding Models
**Want to modify the Staff model?**
- Location: `dashboard_app/models/staff.py`

**Want to see all models?**
- Check: `dashboard_app/models/__init__.py` (central index)

```
Models Location: dashboard_app/models/
├── staff.py          → Staff data structure
├── supplier.py       → Supplier data structure
└── funding.py        → Financial data structures
```

---

### Finding Views/Logic
**Want to edit staff list functionality?**
- Location: `dashboard_app/views/staff.py`
- Function: `staff_list(request)`

**Want to modify expense reports?**
- Location: `dashboard_app/views/reports.py` 
- Function: `expense_report(request)`

```
Views Location: dashboard_app/views/
├── staff.py          → Staff CRUD views (list, add, edit, delete)
├── supplier.py       → Supplier CRUD views
├── funding.py        → Fund/Bank operations
├── reports.py        → Analytics & exports
└── dashboard.py      → Main dashboard view
```

---

### Finding Forms
**Want to modify the staff form?**
- Location: `dashboard_app/forms/staff.py`
- Class: `StaffForm`

```
Forms Location: dashboard_app/forms/
├── staff.py          → StaffForm
├── supplier.py       → SupplierForm
└── funding.py        → FundSourceForm, BankStatementForm
```

---

### Finding Templates
**Want to edit the staff list template?**
- Old path: `templates/staff_list.html` (will be moved)
- New path: `templates/staff/list.html` (after migration)

**Want to edit a report?**
- New path: `templates/reports/expenses_report.html`

```
Templates Location: dashboard_app/templates/
├── base.html                    → Master layout (all pages inherit)
├── dashboard.html               → Dashboard page
├── staff/
│   ├── list.html               → Staff listing page
│   ├── form.html               → Add/Edit staff page
│   └── confirm_delete.html     → Delete confirmation page
├── supplier/
│   ├── list.html
│   ├── form.html
│   └── confirm_delete.html
├── funding/
│   ├── fund_sources.html
│   ├── fund_source_form.html
│   ├── bank_statement.html
│   └── bank_statement_form.html
└── reports/
    ├── expenses_report.html
    ├── mooe_report.html
    ├── fund_report.html
    ├── negosyo_center_report.html
    └── allocations/
        ├── disbursement_table.html
        └── [6 other table files]
```

---

### Finding CSS/Styling
**Want to update forms styling?**
- Location: `static/dashboard_app/css/components/form.css`

**Want to update tables styling?**
- Location: `static/dashboard_app/css/components/table.css`

**Want to update base layout styles?**
- Location: `static/dashboard_app/css/layouts/base.css`

```
Static Files Location: dashboard_app/static/dashboard_app/
css/
├── layouts/
│   ├── base.css        → Main page structure
│   └── sidebar.css     → Sidebar styling
├── components/
│   ├── form.css        → Form elements styling
│   └── table.css       → Table styling
└── pages/
    └── report.css      → Report page styles

js/
├── modules/
│   ├── app.js          → Main app functionality
│   ├── expenses.js     → Expense report logic
│   └── table.js        → Table interactions
```

---

## 🔍 Common Tasks

### Add a New Feature (e.g., Document Management)
1. Create model: `models/document.py`
2. Create form: `forms/document.py`
3. Create views: `views/document.py`
4. Create templates: `templates/document/` folder
5. Add route in `urls.py`
6. Register model in `admin.py`

### Modify Staff Form
1. Open: `forms/staff.py`
2. Edit: `StaffForm` class
3. Add fields/widgets as needed

### Update Staff List View
1. Open: `views/staff.py`
2. Edit: `staff_list()` function
3. Update template reference if needed
4. Template: `templates/staff/list.html`

### Add New CSS for a Component
1. Create: `static/dashboard_app/css/components/my_component.css`
2. Import in template: `{% static 'dashboard_app/css/components/my_component.css' %}`
3. Add CSS rules

### Add New JavaScript Module
1. Create: `static/dashboard_app/js/modules/my_feature.js`
2. Load in template: `<script src="{% static 'dashboard_app/js/modules/my_feature.js' %}"></script>`
3. Write your JavaScript

---

## 📂 File Naming Conventions

**Models:**
- Use singular, descriptive names: `staff.py`, `supplier.py`
- Class names in PascalCase: `class Staff(models.Model)`

**Views:**
- Use singular, descriptive names: `staff.py`, `reports.py`
- Function names in snake_case: `def staff_list()`, `def expense_report()`

**Forms:**
- Match model names: `staff.py`, `supplier.py`
- Class names: `StaffForm`, `SupplierForm`

**Templates:**
- Group in feature folders: `staff/`, `supplier/`, `reports/`
- Use semantic names: `list.html`, `form.html`, `confirm_delete.html`

**Static Files:**
- Organize by purpose: `layouts/`, `components/`, `pages/`, `modules/`
- Lowercase with hyphens: `my-component.css`, `my-feature.js`

---

## 🔗 Quick Links to Key Files

| Purpose | Location |
|---------|----------|
| Staff Model | `models/staff.py` |
| Staff Views | `views/staff.py` |
| Staff Form | `forms/staff.py` |
| Staff Templates | `templates/staff/` |
| Supplier Model | `models/supplier.py` |
| Supplier Views | `views/supplier.py` |
| Supplier Form | `forms/supplier.py` |
| Supplier Templates | `templates/supplier/` |
| Report Views | `views/reports.py` |
| Report Templates | `templates/reports/` |
| Base Layout | `templates/base.html` |
| Base CSS | `static/.../css/layouts/base.css` |
| Components CSS | `static/.../css/components/` |
| Main JS | `static/.../js/modules/app.js` |
| Admin Setup | `admin.py` |
| URL Routing | `urls.py` |
| Settings | `fundmonitor/settings.py` |

---

## 📋 Checklist for First Time

- [ ] Run migration script: `python migrate_files.py`
- [ ] Update template paths in HTML files if using old static file paths
- [ ] Test the website: `python manage.py runserver`
- [ ] Verify all pages load correctly
- [ ] Verify CSS/JS files are loaded
- [ ] Read `ORGANIZATION_GUIDE.md` for detailed structure
- [ ] Review `BEFORE_AFTER_COMPARISON.md` for benefits

---

## 💬 Need Help?

- **Structure questions?** → See `ORGANIZATION_GUIDE.md`
- **Migration help?** → See `SETUP_COMPLETE.md`
- **Benefits explanation?** → See `BEFORE_AFTER_COMPARISON.md`
- **File locations?** → See this guide (quick reference)

---

## ⚡ Pro Tips

1. **Use IDE navigation** - Most IDEs can search files and jump to definitions
2. **Follow the pattern** - When adding new features, follow the structure you see
3. **Keep it consistent** - Use same naming patterns throughout
4. **Use the __init__.py files** - They're designed to make imports convenient
5. **Template inheritance** - Use `{% extends 'base.html' %}` in all feature templates
6. **CSS specificity** - Keep component CSS modular and not too specific
7. **JavaScript modules** - Each module should handle one feature

---

Happy developing! Your codebase is now organized and ready to scale! 🚀
