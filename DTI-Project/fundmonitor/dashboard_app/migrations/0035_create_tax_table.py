# Generated manually: only creates the TaxTable model added for tax lookup
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0034_auto_sync_cheque_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Descriptive name for the tax row (e.g. VGoods, NVService)', max_length=100, unique=True)),
                ('vat_goods_5', models.CharField(help_text='Code/description for VAT goods (5%)', max_length=50, blank=True)),
                ('vat_services_5', models.CharField(help_text='Code/description for VAT services (5%)', max_length=50, blank=True)),
                ('vat_goods_services_3', models.CharField(help_text='Code/description for VAT goods & services (3%)', max_length=50, blank=True)),
                ('vat_goods_1', models.CharField(help_text='Code/description for VAT goods (1%)', max_length=50, blank=True)),
                ('vat_services_2', models.CharField(help_text='Code/description for VAT services (2%)', max_length=50, blank=True)),
                ('vat_rental_5', models.CharField(help_text='Code/description for VAT rental (5%)', max_length=50, blank=True)),
                ('vat_prof_fee_10', models.CharField(help_text='Code/description for VAT professional fee (10%)', max_length=50, blank=True)),
                ('pt_code', models.CharField(help_text='Percentage tax (PT) code or amount', max_length=50, blank=True)),
                ('ewt_code', models.CharField(help_text='Expanded withholding tax (EWT) code or amount', max_length=50, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Tax Table Entry',
                'verbose_name_plural': 'Tax Table Entries',
            },
        ),
    ]
