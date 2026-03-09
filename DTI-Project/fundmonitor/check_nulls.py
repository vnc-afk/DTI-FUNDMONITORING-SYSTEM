import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundmonitor.settings')
django.setup()
from dashboard_app.models import MasterFundMonitoring

records = MasterFundMonitoring.objects.values()
for r in records:
    null_fields = [k for k, v in r.items() if v is None]
    if null_fields:
        print(f"ID {r['id']}: {null_fields}")
