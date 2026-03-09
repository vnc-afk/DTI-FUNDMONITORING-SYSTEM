import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundmonitor.settings')
django.setup()
from dashboard_app.models import MasterFundMonitoring
print(f"Total records: {MasterFundMonitoring.objects.count()}")
for record in MasterFundMonitoring.objects.all():
    print(f"ID {record.id}: transaction_type='{record.transaction_type}'")
