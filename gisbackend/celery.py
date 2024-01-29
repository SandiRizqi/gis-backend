from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gisbackend.settings')

app = Celery('gisCelery')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Jakarta')
app.config_from_object(settings, namespace='CELERY')
app.conf.beat_schedule = {
    'update-deforestations' : {
        'task': 'api.tasks.update_deforestations',
        'schedule' : crontab(minute='*/25')
    },
    'add-hotspot' : {
        'task': 'api.tasks.add_hotspot',
        'schedule' : crontab(minute='*/10')
    },
    'update-hotspots-alert' : {
        'task': 'api.tasks.update_hotspots',
        'schedule' : crontab(minute='*/15')
    },
    'deactivate-hotspots-alert' : {
        'task': 'api.tasks.deactivate_hotspots',
        'schedule' : crontab(minute=0, hour=0)
    }
}
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
