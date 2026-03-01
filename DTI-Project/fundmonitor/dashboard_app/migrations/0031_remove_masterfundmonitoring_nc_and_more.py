# Migration to finalize nc field change - remove old field and rename new field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0030_migrate_nc_data'),
    ]

    operations = [
        # Remove old nc CharField field
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='nc',
        ),
        # Rename nc_negosyo_center to nc
        migrations.RenameField(
            model_name='masterfundmonitoring',
            old_name='nc_negosyo_center',
            new_name='nc',
        ),
        # Update the field properties (related_name)
        migrations.AlterField(
            model_name='masterfundmonitoring',
            name='nc',
            field=models.ForeignKey(
                blank=True,
                help_text='Negosyo Center',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='monitoring_records',
                to='dashboard_app.negosyocenter'
            ),
        ),
    ]
