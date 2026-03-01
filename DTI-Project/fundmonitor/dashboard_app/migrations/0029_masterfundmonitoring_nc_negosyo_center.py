# Migration to change nc field from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0028_district_negosyocenter'),
    ]

    operations = [
        # Add new nc_negosyo_center field as ForeignKey
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='nc_negosyo_center',
            field=models.ForeignKey(
                blank=True,
                help_text='Negosyo Center',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='monitoring_records_new',
                to='dashboard_app.negosyocenter'
            ),
        ),
        # Data migration will happen via RunPython in next migration
    ]
