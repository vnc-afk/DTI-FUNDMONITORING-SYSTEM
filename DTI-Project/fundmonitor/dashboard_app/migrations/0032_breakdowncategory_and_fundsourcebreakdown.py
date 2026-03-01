# Single clean migration for BreakdownCategory and FundSourceBreakdown refactor

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0031_remove_masterfundmonitoring_nc_and_more'),
    ]

    operations = [
        # Create BreakdownCategory model
        migrations.CreateModel(
            name='BreakdownCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Category code (e.g., OO1, 4.1A)', max_length=10, unique=True)),
                ('name', models.CharField(help_text='Category description', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Additional details', null=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('is_active', models.BooleanField(default=True, help_text='Is this category active?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Breakdown Category',
                'verbose_name_plural': 'Breakdown Categories',
                'ordering': ['order', 'code'],
            },
        ),
        # Remove unique_together from FundSourceBreakdown to drop the old constraint
        migrations.AlterUniqueTogether(
            name='fundsourcebreakdown',
            unique_together=set(),
        ),
        # Remove old category CharField field
        migrations.RemoveField(
            model_name='fundsourcebreakdown',
            name='category',
        ),
        # Add new category FK field (nullable initially for existing records)
        migrations.AddField(
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
