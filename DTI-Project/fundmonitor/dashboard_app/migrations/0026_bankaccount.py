# Generated migration for BankAccount and BankStatement auto-balance feature

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0025_fundsourcebreakdown'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Bank account name', max_length=255, unique=True)),
                ('account_number', models.CharField(help_text='Bank account number', max_length=50, unique=True)),
                ('opening_balance', models.DecimalField(decimal_places=2, default=0, help_text='Opening balance for the account', max_digits=15)),
                ('is_active', models.BooleanField(default=True, help_text='Is this account currently active?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Bank Account',
                'verbose_name_plural': 'Bank Accounts',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='bankstatement',
            name='bank_account',
            field=models.ForeignKey(default=None, help_text='Associated bank account', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statements', to='dashboard_app.bankaccount'),
        ),
        migrations.AlterField(
            model_name='bankstatement',
            name='balance',
            field=models.DecimalField(decimal_places=2, editable=False, help_text='Account balance (auto-calculated)', max_digits=15),
        ),
        migrations.AlterUniqueTogether(
            name='bankstatement',
            unique_together={('bank_account', 'date', 'description', 'debit', 'credit')},
        ),
        migrations.AlterModelOptions(
            name='bankstatement',
            options={'ordering': ['date', 'created_at'], 'verbose_name': 'Bank Statement', 'verbose_name_plural': 'Bank Statements'},
        ),
    ]
