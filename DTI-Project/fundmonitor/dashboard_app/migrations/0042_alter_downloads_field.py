# Migration to convert downloads field to DecimalField

from django.db import migrations, models
import dashboard_app.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0041_add_dv_downloads'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterfundmonitoring',
            name='downloads',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Downloads amount',
                max_digits=15,
                null=True,
                validators=[dashboard_app.validators.validate_transaction_amount]
            ),
        ),
    ]
