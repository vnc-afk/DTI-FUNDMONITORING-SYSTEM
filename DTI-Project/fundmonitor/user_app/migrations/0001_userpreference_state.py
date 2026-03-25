from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('dark', 'Dark Theme'), ('light', 'Light Theme')], default='dark', max_length=10)),
                ('notifications_enabled', models.BooleanField(default=True)),
                ('items_per_page', models.IntegerField(default=25)),
                ('password_changed', models.BooleanField(default=False, help_text='Whether user has changed their initial password')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='preference', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_userpreference',
            },
        ),
    ]
