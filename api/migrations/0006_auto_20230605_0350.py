# Generated by Django 3.2.1 on 2023-06-05 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_fire_events_alert_list_event_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='fire_events_alert_list',
            name='LAT',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='fire_events_alert_list',
            name='LONG',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True),
        ),
    ]
