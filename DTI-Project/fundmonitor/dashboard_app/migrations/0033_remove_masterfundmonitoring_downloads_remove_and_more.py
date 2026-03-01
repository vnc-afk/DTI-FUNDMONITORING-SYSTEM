# Migration for removing downloads, dv_number fields and changing cheque_status to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0032_breakdowncategory_and_fundsourcebreakdown'),
    ]

    operations = [
        # Remove downloads field
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='downloads',
        ),
        # Remove dv_number field
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='dv_number',
        ),
        # Remove old cheque_status CharField
        migrations.RemoveField(
            model_name='masterfundmonitoring',
            name='cheque_status',
        ),
        # Add new cheque_status as ForeignKey to BankStatement
        migrations.AddField(
            model_name='masterfundmonitoring',
            name='cheque_status',
            field=models.ForeignKey(
                blank=True,
                help_text='Link to bank statement status',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='monitoring_records_status',
                to='dashboard_app.bankstatement'
            ),
        ),
        # Update FundSourceBreakdown category to be nullable
        migrations.AlterField(
            model_name='fundsourcebreakdown',
            name='category',
            field=models.ForeignKey(
                blank=True,
                help_text='Breakdown category',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fund_breakdowns',
                to='dashboard_app.breakdowncategory'
            ),
        ),
    ]
