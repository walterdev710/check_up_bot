# Generated by Django 5.1.7 on 2025-03-13 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='username',
            new_name='full_name',
        ),
    ]
