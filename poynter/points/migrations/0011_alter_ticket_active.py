# Generated by Django 5.2.1 on 2025-06-24 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0010_ticket_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='active',
            field=models.BooleanField(default=False, help_text='The active ticket for this project is the one being voted on. Only one ticket may be marked active per voting session at a time.', null=True),
        ),
    ]
