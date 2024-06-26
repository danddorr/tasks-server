# Generated by Django 5.0.6 on 2024-06-17 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_api', '0008_task_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=20, unique=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(choices=[('Creator', 'Creator'), ('Viewer', 'Viewer'), ('Editor', 'Editor')], default='Viewer', max_length=10)),
                ('tasklist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='todo_api.tasklist')),
            ],
        ),
    ]
