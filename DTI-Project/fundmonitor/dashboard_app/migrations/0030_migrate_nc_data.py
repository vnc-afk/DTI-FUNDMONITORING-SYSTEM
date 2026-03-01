# Data migration to convert nc CharField to ForeignKey

from django.db import migrations


def migrate_nc_data(apps, schema_editor):
    """Migrate nc data from CharField to ForeignKey"""
    MasterFundMonitoring = apps.get_model('dashboard_app', 'MasterFundMonitoring')
    NegosyoCenter = apps.get_model('dashboard_app', 'NegosyoCenter')
    
    # Get all records with old nc values
    records = MasterFundMonitoring.objects.all()
    
    for record in records:
        if record.nc:
            # Try to find matching NegosyoCenter by code
            try:
                nc_obj = NegosyoCenter.objects.get(code=record.nc.lower())
                record.nc_negosyo_center = nc_obj
                record.save(update_fields=['nc_negosyo_center'])
            except NegosyoCenter.DoesNotExist:
                # If no exact match, try to find by name
                try:
                    nc_obj = NegosyoCenter.objects.get(name__iexact=record.nc)
                    record.nc_negosyo_center = nc_obj
                    record.save(update_fields=['nc_negosyo_center'])
                except (NegosyoCenter.DoesNotExist, NegosyoCenter.MultipleObjectsReturned):
                    # Log but don't fail - leave as NULL
                    pass


def reverse_migrate_nc_data(apps, schema_editor):
    """Reverse migration - clear nc_negosyo_center field"""
    MasterFundMonitoring = apps.get_model('dashboard_app', 'MasterFundMonitoring')
    MasterFundMonitoring.objects.all().update(nc_negosyo_center=None)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0029_masterfundmonitoring_nc_negosyo_center'),
    ]

    operations = [
        migrations.RunPython(migrate_nc_data, reverse_migrate_nc_data),
    ]
