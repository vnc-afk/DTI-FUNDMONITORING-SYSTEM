# Generated migration to add DV No. and Downloads fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0040_make_mooe_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='dv_number',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                help_text='Disbursement Voucher number'
            ),
        ),
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='downloads',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                help_text='Downloads information'
            ),
        ),
    ]
