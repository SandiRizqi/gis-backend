# Generated by Django 3.2.1 on 2024-03-14 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20240314_0930'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deforestations_events_alert_list',
            old_name='HA',
            new_name='AREA',
        ),
    ]
