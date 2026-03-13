# Generated migration to make fund_source nullable

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0043_alter_supplier_contact_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterfundmonitoring',
            name='fund_source',
            field=models.ForeignKey(
                blank=True,
                help_text='Fund source for transaction',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='monitoring_records',
                to='dashboard_app.fundsource'
            ),
        ),
    ]
