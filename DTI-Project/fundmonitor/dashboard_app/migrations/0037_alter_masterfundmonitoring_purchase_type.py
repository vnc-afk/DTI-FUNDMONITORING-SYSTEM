# Generated migration to change purchase_type from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0036_purchasetype_taxtable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='purchase_type',
        ),
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='purchase_type',
            field=models.ForeignKey(
                blank=True,
                help_text='Type of purchase with associated tax rates',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='monitoring_records',
                to='dashboard_app.purchasetype'
            ),
        ),
    ]
