# Generated migration for contact_number field width

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0042_alter_downloads_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='contact_number',
            field=models.CharField(blank=True, max_length=30, null=True, help_text='Philippine phone number format'),
        ),
    ]
