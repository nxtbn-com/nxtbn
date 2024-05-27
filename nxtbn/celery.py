from __future__ import absolute_import, unicode_literals
import logging
import os
from celery import Celery
from datetime import timedelta

'''
Command:
celery -A nxtbn worker --loglevel=info
celery -A nxtbn beat --loglevel=info
'''

# Set the default Django settings module for the 'celery' config instead of putting the celery config here.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')

# Initialize Celery
app = Celery('nxtbn')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def log_task_request(self):
    """Logs the details of the current task request for debugging purposes."""
    logger = logging.getLogger(__name__)
    logger.info('Task Request: %s', self.request)