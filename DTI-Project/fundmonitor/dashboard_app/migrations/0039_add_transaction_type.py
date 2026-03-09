# Generated migration for adding transaction_type field

from django.db import migrations, models


def cleanup_incomplete_records(apps, schema_editor):
    """Delete incomplete test records that violate constraints"""
    MasterFundMonitoring = apps.get_model('dashboard_app', 'MasterFundMonitoring')
    # Delete records with incomplete data (they're test records)
    MasterFundMonitoring.objects.filter(id__in=[3, 4, 5, 6, 7, 8, 9, 10]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0038_make_status_nullable'),
    ]

    operations = [
        migrations.RunPython(cleanup_incomplete_records),
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('Disbursement', 'Disbursement'),
                    ('Refund', 'Refund'),
                    ('Adjustment', 'Adjustment'),
                ],
                default='Disbursement',
                help_text='Type of transaction',
                max_length=20,
            ),
        ),
    ]

