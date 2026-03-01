# Migration to change cheque_status back to CharField and set up auto-sync

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0033_remove_masterfundmonitoring_downloads_remove_and_more'),
    ]

    operations = [
        # Remove the old ForeignKey cheque_status field
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='cheque_status',
        ),
        # Add new cheque_status as CharField with choices
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='cheque_status',
            field=models.CharField(
                choices=[('Pending', 'Pending'), ('Cleared', 'Cleared'), ('Bounced', 'Bounced')],
                default='Pending',
                help_text='Cheque/Payment status',
                max_length=20
            ),
        ),
    ]
