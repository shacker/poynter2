# Generated by Django 5.2.1 on 2025-06-24 22:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0011_alter_ticket_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PointingSession',
            new_name='Space',
        ),
    ]
