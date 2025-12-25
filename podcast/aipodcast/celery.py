import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_hunt.settings")

app = Celery("job_hunt")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
