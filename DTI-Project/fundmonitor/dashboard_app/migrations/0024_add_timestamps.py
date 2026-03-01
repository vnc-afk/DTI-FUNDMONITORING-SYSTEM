# Generated migration to add missing timestamp fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0023_division_alter_masterfundmonitoring_division_and_more'),
    ]

    operations = [
        # Add created_at and updated_at to Supplier
        migrations.AddField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Add created_at and updated_at to BankStatement
        migrations.AddField(
            model_name='bankstatement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bankstatement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Add created_at and updated_at to FundSource
        migrations.AddField(
            model_name='fundsource',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundsource',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Add created_at and updated_at to Staff
        migrations.AddField(
            model_name='staff',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
