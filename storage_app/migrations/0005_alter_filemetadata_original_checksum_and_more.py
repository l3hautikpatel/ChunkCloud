# Generated by Django 5.1.6 on 2025-03-11 06:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage_app', '0004_alter_filechunk_options_alter_filemetadata_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='filemetadata',
            name='original_checksum',
            field=models.CharField(help_text='Checksum of the complete original file and updated in the checksum function', max_length=64, null=True),
        ),
        migrations.CreateModel(
            name='FileOperationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('operation_type', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file_id', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
