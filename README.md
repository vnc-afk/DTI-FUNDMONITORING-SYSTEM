# DTI Fund Monitoring System

A comprehensive Django-based web application for monitoring and managing fund allocation, tracking expenses, and managing suppliers and financial transactions for the Department of Trade and Industry (DTI).

## Overview

The DTI Fund Monitoring System is designed to streamline financial management processes by providing:
- **Fund Source Management**: Track and manage various funding sources
- **Expense Tracking**: Monitor expenses with proper categorization and classification
- **Supplier Management**: Maintain supplier information with VAT status and categorization
- **Bank Statement Processing**: Import and reconcile bank statements
- **Dashboard Analytics**: Real-time insights into fund allocation and spending patterns
- **Staff Management**: Manage staff information and access control

## Tech Stack

- **Backend**: Django 6.0.2
- **Database**: PostgreSQL (with SQLite for development)
- **Task Queue**: Celery with Redis
- **Data Processing**: Pandas, NumPy
- **File Handling**: OpenpyXL for Excel operations
- **Server**: ASGI/WSGI compatible
- **Frontend**: Django Templates

## Project Structure

```
DTI-Project/
├── fundmonitor/              # Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── core/                     # Core application
│   ├── models.py            # Core data models
│   ├── views.py             # Core views
│   └── migrations/          # Database migrations
├── dashboard_app/           # Main dashboard application
│   ├── models/              # Data models (bank, supplier, funds, etc.)
│   ├── views/               # Dashboard views
│   ├── forms/               # Form definitions
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── migrations/          # Database migrations
└── db.sqlite3               # SQLite database (development)
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+
- Redis (for Celery task queue)
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DTI-FUNDMONITORING-SYSTEM.git
   cd DTI-FUNDMONITORING-SYSTEM
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (if needed)
   - Copy `.env.example` to `.env`
   - Update database credentials and other settings

5. **Run migrations**
   ```bash
   cd DTI-Project/fundmonitor
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

## Running the Application

### Development Server
```bash
cd DTI-Project/fundmonitor
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Production Server
```bash
python run_server.py
```

### Running Celery (for background tasks)
```bash
celery -A fundmonitor worker -l info
```

### Running Celery Beat (for scheduled tasks)
```bash
celery -A fundmonitor beat -l info
```

## Key Features

### Fund Management
- Create and track multiple fund sources
- Monitor fund allocation across projects
- Generate fund utilization reports

### Expense Management
- Categorize expenses with proper classification
- Track expense objects and accounting codes
- Generate expense analysis reports

### Supplier Management
- Maintain comprehensive supplier database
- Track supplier categories and VAT status
- Monitor supplier transactions

### Bank Reconciliation
- Import bank statements
- Automatic reconciliation matching
- Transaction verification and validation

### Dashboard Analytics
- Real-time fund monitoring
- Expense trend analysis
- Supplier performance metrics
- Interactive charts and visualizations

## Database Management

### Initial Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Verification Scripts
```bash
python check_nulls.py          # Check for NULL values in database
python verify_transaction_type.py  # Verify transaction types
python migrate_files.py         # Migrate file uploads
```

## API Endpoints

The system is built with Django and follows standard RESTful patterns. Main endpoints include:
- `/admin` - Django admin interface
- `/dashboard` - Main dashboard
- `/suppliers` - Supplier management
- `/funds` - Fund management
- `/expenses` - Expense tracking
- `/bank-statements` - Bank reconciliation

## Configuration

Key settings in `fundmonitor/settings.py`:
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Configure for your domain
- `DATABASES`: PostgreSQL connection settings
- `CELERY_BROKER_URL`: Redis connection for Celery

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify database credentials in settings
- Check database exists: `createdb fundmonitor`

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL` in settings

### Celery Tasks Not Running
- Ensure Redis is running
- Check Celery worker logs
- Verify `CELERY_BROKER_URL` in settings

## Security Considerations

- Always use a strong `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Use environment variables for sensitive data
- Configure HTTPS and CSRF protection
- Regularly update dependencies

## Performance Optimization

- Enable caching with Redis
- Use database indexes on frequently queried fields
- Implement pagination for large datasets
- Use Celery for long-running tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the GitHub repository.

## Authors

Vince & Nard & VNard & Nardince & Levince

## Changelog

### Version 1.0.0
- Initial release
- Core fund monitoring functionality
- Dashboard and reporting features
- Bank reconciliation system