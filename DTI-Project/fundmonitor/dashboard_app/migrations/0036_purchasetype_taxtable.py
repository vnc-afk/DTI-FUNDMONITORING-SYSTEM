# Generated migration for PurchaseType and TaxTable update

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0035_create_tax_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Purchase type name', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Is this purchase type active?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Purchase Type',
                'verbose_name_plural': 'Purchase Types',
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='taxtable',
            name='ewt_code',
        ),
        migrations.RemoveField(
            model_name='taxtable',
            name='name',
        ),
        migrations.RemoveField(
            model_name='taxtable',
            name='pt_code',
        ),
        migrations.AddField(
            model_name='taxtable',
            name='purchase_type',
            field=models.ForeignKey(help_text='Purchase type for this tax entry', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tax_entries', to='dashboard_app.purchasetype'),
        ),
        migrations.AlterUniqueTogether(
            name='taxtable',
            unique_together={('purchase_type',)},
        ),
    ]
