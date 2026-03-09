# Generated migration to make mooe field nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0039_add_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterfundmonitoring',
            name='mooe',
            field=models.CharField(
                blank=True,
                help_text='MOOE category code',
                max_length=100,
                null=True,
                validators=[],  # Add validators if needed
            ),
        ),
    ]
