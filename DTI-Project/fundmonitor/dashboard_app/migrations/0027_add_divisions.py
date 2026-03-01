from django.db import migrations


def add_divisions(apps, schema_editor):
    """Add predefined divisions"""
    Division = apps.get_model('dashboard_app', 'Division')
    
    divisions = ['BDD', 'CPD', 'FAD']
    for division_name in divisions:
        Division.objects.get_or_create(
            name=division_name,
            defaults={'is_active': True, 'description': f'{division_name} Division'}
        )


def remove_divisions(apps, schema_editor):
    """Remove divisions if migration is reversed"""
    Division = apps.get_model('dashboard_app', 'Division')
    Division.objects.filter(name__in=['BDD', 'CPD', 'FAD']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0026_bankaccount'),
    ]

    operations = [
        migrations.RunPython(add_divisions, remove_divisions),
    ]
