# Generated migration for FundSourceBreakdown model

from django.db import migrations, models
import django.db.models.deletion
import dashboard_app.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0024_add_timestamps'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundSourceBreakdown',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[
                        ('OO1', 'OO1 - Personnel Services'),
                        ('OO2', 'OO2 - Maintenance & Other Operating Expenses'),
                        ('OO3', 'OO3 - Financial Expenses'),
                        ('4.1A', '4.1A - Capital Outlay (Equipment)'),
                        ('4.1B', '4.1B - Capital Outlay (Infrastructure)'),
                        ('4.2', '4.2 - Other Capital Outlays'),
                    ],
                    help_text='Breakdown category',
                    max_length=10
                )),
                ('budget_amount', models.DecimalField(
                    decimal_places=2,
                    help_text='Budget allocation for this category',
                    max_digits=15,
                    validators=[dashboard_app.validators.validate_transaction_amount]
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fund_source', models.ForeignKey(
                    help_text='Associated fund source',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='breakdowns',
                    to='dashboard_app.fundsource'
                )),
            ],
            options={
                'verbose_name': 'Fund Source Breakdown',
                'verbose_name_plural': 'Fund Source Breakdowns',
                'ordering': ['fund_source', 'category'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='fundsourcebreakdown',
            unique_together={('fund_source', 'category')},
        ),
    ]
