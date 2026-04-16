# Backend Structure

Generated on: 2026-04-16 11:10:30

This file summarizes the Django backend located in DTI-Project/backend.

```text
backend/
|-- manage.py
|-- db.sqlite3
|-- package.json
|-- requirements.txt
|-- BACKEND_FILE_STRUCTURE.md
|-- fundmonitor/
|   |-- __init__.py
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- bank_statement_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- serializers.py
|   |-- signals.py
|   |-- tests.py
|   |-- urls.py
|   |-- views.py
|   `-- migrations/
|-- dashboard_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- api_urls.py
|   |-- api_views.py
|   |-- apps.py
|   |-- consumers.py
|   |-- middleware.py
|   |-- realtime.py
|   |-- routing.py
|   |-- serializers.py
|   |-- signals.py
|   |-- tests.py
|   |-- urls.py
|   |-- management/
|   |-- migrations/
|   |-- models/
|   |-- templatetags/
|   |-- utils/
|   `-- views/
|-- data_management_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- api_urls.py
|   |-- api_views.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   |-- views.py
|   |-- management/
|   `-- migrations/
|-- mater_fundmonitor_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- api_urls.py
|   |-- api_views.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   |-- views.py
|   `-- migrations/
|-- reports_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- api_urls.py
|   |-- api_views.py
|   |-- apps.py
|   |-- models.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   |-- views.py
|   `-- migrations/
`-- user_app/
    |-- __init__.py
    |-- admin.py
    |-- api_auth_views.py
    |-- api_urls.py
    |-- api_views.py
    |-- apps.py
    |-- forms.py
    |-- models.py
    |-- pagination.py
    |-- serializers.py
    |-- tests.py
    |-- urls.py
    |-- utils.py
    |-- views.py
    `-- migrations/
```

## Notes

- fundmonitor/ contains the Django project settings and root URL config.
- Each app keeps its own forms, views, models, tests, serializers, urls, and migrations.
- This summary intentionally omits cache folders and environment artifacts (for readability).
