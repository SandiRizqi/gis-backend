# Generated by Django 3.2.1 on 2023-07-26 02:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_fire_events_alert_list_update_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='fire_hotspot',
            name='UPDATE_TIME',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
