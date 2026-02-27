import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundmonitor.settings')
django.setup()

from dashboard_app.models import BankStatement
from datetime import datetime, timedelta

# Delete existing statements if any
BankStatement.objects.all().delete()

# Create sample data
today = datetime.now().date()

BankStatement.objects.create(
    date=today,
    description='Online Transfer - Payroll',
    check_number='CHK-00421',
    debit=0,
    credit=85000.00,
    balance=128350.00,
    status='Cleared'
)

BankStatement.objects.create(
    date=today - timedelta(days=3),
    description='Utility Payment - Meralco',
    check_number='CHK-00420',
    debit=4320.00,
    credit=0,
    balance=43350.00,
    status='On Process'
)

BankStatement.objects.create(
    date=today - timedelta(days=7),
    description='Supplier Payment - Office Supplies',
    check_number='CHK-00419',
    debit=12750.00,
    credit=0,
    balance=47670.00,
    status='Cleared'
)

BankStatement.objects.create(
    date=today - timedelta(days=11),
    description='Client Invoice - Project Alpha',
    check_number='CHK-00418',
    debit=0,
    credit=171800.00,
    balance=80420.00,
    status='Cleared'
)

print("✓ Added 4 sample bank statements")
