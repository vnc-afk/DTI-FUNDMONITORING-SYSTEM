# DTI Fund Monitoring System

A Django-based financial monitoring platform for the Department of Trade and Industry (DTI), designed to manage fund sources, monitor expenses, reconcile bank records, and generate operational dashboards.

## Overview

The system centralizes financial operations across multiple modules:

- Fund source and allocation tracking
- Expense recording with classification and reporting support
- Supplier profiling and transaction monitoring
- Bank statement import and reconciliation workflows
- Role-aware dashboards and activity logging
- User and staff account management

## Technology Stack

- Backend framework: Django 6.0.2
- Database: PostgreSQL (configured as default)
- Async/background processing: Celery 5.6.2 with Redis
- Data tools: Pandas 3.0.1 and NumPy 2.4.2
- Excel processing: OpenPyXL 3.1.5
- Production serving: Waitress (via batch launcher)
- Frontend: Django templates + static assets

## Repository Structure

```text
DTI-FUNDMONITORING-SYSTEM/
|-- README.md
|-- requirements.txt
|-- start_fundmonitor.bat
`-- DTI-Project/
    `-- fundmonitor/
        |-- manage.py
        |-- fundmonitor/               # project settings, urls, wsgi, asgi
        |-- dashboard_app/             # dashboard, middleware, utilities
        |-- mater_fundmonitor_app/     # core fund monitoring workflows
        |-- bank_statement_app/        # bank statement handling
        |-- data_management_app/       # data maintenance and admin workflows
        |-- reports_app/               # report generation and exports
        |-- user_app/                  # authentication and user management
        |-- templates/                 # shared templates
        |-- static/                    # project-level static files
        `-- staticfiles/               # collected static output
```

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis (required for Celery worker/beat)
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
pip install -r requirements.txt
```

### 4. Configure database settings

Edit `DTI-Project/fundmonitor/fundmonitor/settings.py` and update `DATABASES['default']` for your local PostgreSQL instance.

### 5. Apply migrations

```bash
cd DTI-Project/fundmonitor
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

### Development mode

From `DTI-Project/fundmonitor`:

```bash
py manage.py runserver
```

Default URL: `http://127.0.0.1:8000`

### Production-style launcher (Windows)

From repository root:

```bat
start_fundmonitor.bat
```

This starts Waitress on `0.0.0.0:8000` and auto-restarts if the process exits.

### Celery worker

From `DTI-Project/fundmonitor`:

```bash
celery -A fundmonitor worker -l info
```

### Celery beat

From `DTI-Project/fundmonitor`:

```bash
celery -A fundmonitor beat -l info
```

## Main Application Areas

- `dashboard_app`: executive and operational dashboards, notifications, activity logs
- `mater_fundmonitor_app`: core fund and transaction domain workflows
- `bank_statement_app`: statement upload and reconciliation support
- `data_management_app`: maintenance of reference and transactional data
- `reports_app`: summary and printable/exportable reporting
- `user_app`: login, account lifecycle, and access management

## URL Routing

URL patterns are composed in `fundmonitor/urls.py` and include app-level routes from:

- `user_app`
- `dashboard_app`
- `mater_fundmonitor_app`
- `bank_statement_app`
- `data_management_app`
- `reports_app`

Admin portal: `/admin/`

## Configuration Notes

Important settings file:

- `DTI-Project/fundmonitor/fundmonitor/settings.py`

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
- Run commands from `DTI-Project/fundmonitor`

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
