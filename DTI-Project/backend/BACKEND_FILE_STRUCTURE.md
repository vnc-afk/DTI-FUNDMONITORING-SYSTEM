# Backend Structure

This file summarizes the Django backend located in DTI-Project/backend.

```text
backend/
|-- .env
|-- .env.render.example
|-- .gitattributes
|-- .gitignore
|-- .venv/
|-- BACKEND_FILE_STRUCTURE.md
|-- CHATBOT_README.md
|-- db.sqlite3
|-- manage.py
|-- package.json
|-- package-lock.json
|-- requirements.txt
|-- staticfiles/
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
|-- chatbot_app/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- chatbot_service.py
|   |-- EXAMPLES.md
|   |-- IMPLEMENTATION_SUMMARY.md
|   |-- INSTALLATION_COMPLETE.md
|   |-- MIGRATIONS_GUIDE.md
|   |-- models.py
|   |-- QUICKSTART.md
|   |-- README.md
|   |-- serializers.py
|   |-- setup.sh
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
|   |-- management/
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
- chatbot_app/ is a specialized Django app integrating AI chatbot functionality with comprehensive documentation (README.md, QUICKSTART.md, IMPLEMENTATION_SUMMARY.md).
- Environment configuration: .env for local development, .env.render.example for render.com deployments.
- This summary intentionally omits cache folders, __pycache__, and other artifacts for readability.
