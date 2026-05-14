# DTI Fund Monitoring System

A Django-based financial monitoring platform for the Department of Trade and Industry (DTI), designed to manage fund sources, monitor expenses, reconcile bank records, and generate operational dashboards.

## Overview

The DTI Fund Monitoring System is a comprehensive financial management platform that centralizes fund operations, transaction tracking, and analytics. Key capabilities include:

**Core Financial Operations:**
- Multi-source fund management with annual budget tracking and allocation breakdowns by category
- Comprehensive transaction recording with DV/check numbers, tax classifications (goods, services, fuel, VAT), and status tracking
- Expense categorization and object-based accounting with hierarchical chart-of-accounts organization
- Bank statement reconciliation with automatic balance calculations and transaction clearing status
- Purchase order tracking with multiple purchase types (Direct, Competitive Bidding, Small Purchase, etc.)

**Master Data & Configuration:**
- Supplier profiling with TIN, VAT status, PhilGEPS registration, and contact information
- Organizational structure management (divisions, staff assignments, negosyo centers, districts)
- Bulk data import capabilities for master records, bank statements, suppliers, and staff (Excel/CSV support)
- Tax configuration and rate management for compliance

**Insights & Reporting:**
- Executive dashboards with real-time fund utilization, budget vs. actual, and year-over-year trends
- Pre-built financial reports: Expense breakdown, MOOE, Negosyo Center summaries, Fund utilization, TIN/supplier analysis
- Comprehensive activity logging with 15+ tracked actions (Create, Update, Delete, View, Download, Import, Login, etc.)
- Archive management with year-wise transaction retrieval and restoration

**User Experience:**
- Role-based access control with JWT authentication and group-based permissions
- AI-powered financial chatbot with 13+ intents for instant data queries (fund status, expense summaries, supplier info, reconciliation status)
- Real-time notifications and activity summaries
- User preference management (theme, notifications, pagination)

## Technology Stack

- Backend framework: Django
- Frontend framework: Vue 3 + Vite
- Database (default): SQLite (`DTI-Project/backend/db.sqlite3`)
- Optional database: PostgreSQL (configure in Django settings)
- Async/background processing: Celery + Redis (optional, if enabled)
- AI/Chatbot: Integrated chatbot service with LLM support
- Data tools: Pandas and NumPy
- Excel processing/export: OpenPyXL (backend) and ExcelJS (frontend)

## Repository Structure

```text
DTI-FUNDMONITORING-SYSTEM/
|-- README.md
`-- DTI-Project/
    |-- backend/
    |   |-- manage.py
    |   |-- requirements.txt
    |   |-- fundmonitor/               # project settings, urls, asgi, wsgi
    |   |-- chatbot_app/
    |   |-- dashboard_app/
    |   |-- mater_fundmonitor_app/
    |   |-- bank_statement_app/
    |   |-- data_management_app/
    |   |-- reports_app/
    |   `-- user_app/
    `-- frontend/
        |-- package.json
        |-- vite.config.js
        |-- src/
        |   |-- pages/
        |   |-- services/
        |   `-- stores/
        `-- ...
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Redis (only if running Celery worker/beat)
- pip

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/DTI-FUNDMONITORING-SYSTEM.git
cd DTI-FUNDMONITORING-SYSTEM
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r DTI-Project/backend/requirements.txt
```

Install frontend dependencies:

```bash
cd DTI-Project/frontend
npm install
cd ../..
```

### 4. Configure database settings

Default database is SQLite and works out of the box.

To use PostgreSQL, edit `DTI-Project/backend/fundmonitor/settings.py` and update `DATABASES['default']`.

### 5. Apply migrations

```bash
cd DTI-Project/backend
py manage.py migrate
```

### 6. Create an admin user

```bash
py manage.py createsuperuser
```

### 7. Collect static files

```bash
py manage.py collectstatic --noinput
```

## Running the System

### Backend (Django API/app)

From `DTI-Project/backend`:

```bash
py manage.py runserver
```

Default URL: `http://127.0.0.1:8000`

### Frontend (Vue + Vite)

From `DTI-Project/frontend`:

```bash
npm run dev
```

Default URL: `http://localhost:5173`

The frontend is configured to call backend endpoints served by Django.

### Celery worker

From `DTI-Project/backend`:

```bash
celery -A fundmonitor worker -l info
```

### Celery beat

From `DTI-Project/backend`:

```bash
celery -A fundmonitor beat -l info
```

## Main Application Areas

- `chatbot_app`: AI-powered chatbot service for financial queries and assistance
- `dashboard_app`: executive and operational dashboards, notifications, activity logs
- `mater_fundmonitor_app`: core fund and transaction domain workflows
- `bank_statement_app`: statement and reconciliation
- `data_management_app`: maintenance of reference and transactional data
- `reports_app`: summary and printable/exportable reporting
- `user_app`: login, account lifecycle, and access management

## URL Routing

URL patterns are composed in `fundmonitor/urls.py` and include app-level routes from:

- `chatbot_app`
- `user_app`
- `dashboard_app`
- `mater_fundmonitor_app`
- `bank_statement_app`
- `data_management_app`
- `reports_app`

Admin portal: `/admin/`

## Configuration Notes

Important settings file:

- `DTI-Project/backend/fundmonitor/settings.py`

Review these before deployment:

- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASES`
- `SESSION_COOKIE_SECURE`

## Troubleshooting

### App cannot connect to database

- Confirm PostgreSQL service is running
- Verify `HOST`, `PORT`, `NAME`, `USER`, and `PASSWORD` in `settings.py`
- Ensure the target database already exists

### Static files are missing or outdated

- Run `py manage.py collectstatic --noinput`
- Verify `STATIC_URL`, `STATICFILES_DIRS`, and `STATIC_ROOT`

### Celery commands fail

- Confirm Redis is running and reachable
- Ensure the virtual environment is active
- Run commands from `DTI-Project/backend`

### Frontend cannot start

- Confirm you are in `DTI-Project/frontend`
- Run `npm install` before `npm run dev`
- Ensure `package.json`, `index.html`, and `vite.config.js` exist in the frontend folder

## Security Checklist for Deployment

- Set `DEBUG = False`
- Move secrets and credentials out of source code
- Use a strong, private `SECRET_KEY`
- Restrict `ALLOWED_HOSTS` to trusted domains/IPs
- Enable HTTPS and secure session/cookie settings

## Contributors

- Vince
- Nard
- VNard
- Nardince
- Levince
- Si workfromhome
