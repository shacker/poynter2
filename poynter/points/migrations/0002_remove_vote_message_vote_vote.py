# Generated by Django 5.2.1 on 2025-06-24 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('points', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='message',
        ),
        migrations.AddField(
            model_name='vote',
            name='vote',
            field=models.SmallIntegerField(default=1, help_text='Numerical vote up to 2 digits'),
            preserve_default=False,
        ),
    ]
