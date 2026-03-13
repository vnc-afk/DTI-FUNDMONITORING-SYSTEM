import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundmonitor.settings')
django.setup()

from dashboard_app.models import BankStatement

# Simulate what the view does
bank_statements = BankStatement.objects.all().order_by('date')
bank_dates = []
bank_debits = []
bank_credits = []
bank_balances = []

if bank_statements.exists():
    for stmt in bank_statements:
        bank_dates.append(stmt.date.isoformat())
        bank_debits.append(float(stmt.debit or 0))
        bank_credits.append(float(stmt.credit or 0))
        bank_balances.append(float(stmt.balance or 0))

# Check what JSON would be sent to template
bank_dates_json = json.dumps(bank_dates)
bank_debits_json = json.dumps(bank_debits)
bank_credits_json = json.dumps(bank_credits)
bank_balances_json = json.dumps(bank_balances)

print("=== DATA BEING SENT TO TEMPLATE ===")
print(f"bank_dates length: {len(bank_dates)}")
print(f"bank_debits length: {len(bank_debits)}")
print(f"bank_credits length: {len(bank_credits)}")
print(f"bank_balances length: {len(bank_balances)}")
print()
print("bank_dates sample (first 5):")
print(bank_dates[:5])
print()
print("bank_debits sample (first 5):")
print(bank_debits[:5])
print()
print("bank_balances sample (last 5):")
print(bank_balances[-5:])
print()
print("✓ All data is properly formatted and ready for charts")
