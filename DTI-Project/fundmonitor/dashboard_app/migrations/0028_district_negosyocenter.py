# Generated migration for District and NegosyoCenter models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0027_add_divisions'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='District name (e.g., District 1, District 2)', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of the district', null=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('is_active', models.BooleanField(default=True, help_text='Is this district active?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'District',
                'verbose_name_plural': 'Districts',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='NegosyoCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Negosyo Center name', max_length=100)),
                ('code', models.CharField(help_text='Unique code for the NC (e.g., sto_domingo)', max_length=50, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of the NC', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Is this NC active?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('district', models.ForeignKey(help_text='Parent district', on_delete=django.db.models.deletion.CASCADE, related_name='negosyo_centers', to='dashboard_app.district')),
            ],
            options={
                'verbose_name': 'Negosyo Center',
                'verbose_name_plural': 'Negosyo Centers',
                'ordering': ['district__order', 'district__name', 'name'],
                'unique_together': {('district', 'code')},
            },
        ),
    ]
