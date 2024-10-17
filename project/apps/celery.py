from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('apps')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


app = Celery('apps', broker=settings.RABBITMQ_URL)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

app.conf.beat_schedule = {
    "check_permission_status": {"task": "apps.users.tasks.check_permission_status", 'schedule': crontab(minute='*/1')},
    "check_buyer_status": {"task": "apps.users.tasks.check_buyer_status", 'schedule': crontab(minute='*/60'),},
    "check_supplier_status": {"task": "apps.users.tasks.check_supplier_status", 'schedule': crontab(minute='*/60')},
    "check_auction_status": {"task": "apps.auctions.tasks.check_status", 'schedule': 30.0,},
    "check_one_pay": {"task": "apps.payment.tasks.check_one_pay", 'schedule': crontab(minute='*/1')},
    "check_user_diamond_sponsor_status": {"task": "apps.users.tasks.check_user_diamond_sponsor_status", 'schedule': crontab(minute='*/1')},
    "check_our_partner_status": {"task": "apps.sale_schema.tasks.check_our_partner_status", 'schedule': crontab(minute='*/1')},
    "check_user_diamond_sponsor_confirm": {"task": "apps.users.tasks.check_user_diamond_sponsor_confirm", 'schedule': timedelta(seconds=30)},
    "check_rfx_seat_available": {"task": "apps.rfx.tasks.check_rfx_seat_available", 'schedule': timedelta(seconds=30)},
    "check_rfx_quote_status": {"task": "apps.rfx.tasks.check_rfx_quote_status", 'schedule': timedelta(seconds=30)},
    "check_rfx_is_full": {"task": "apps.rfx.tasks.check_rfx_is_full", 'schedule': crontab(minute='*/1')},
    "send_mail_auto_nego": {"task": "apps.rfx.tasks.send_mail_auto_nego", 'schedule': crontab(minute='*/1')},
    "rfx_send_mail_invitation_NPDOC4": {"task": "apps.rfx.tasks.rfx_send_mail_invitation_NPDOC4", 'schedule': crontab(minute='*/1')},
    "check_rfx_due_date_expired": {"task": "apps.rfx.tasks.check_rfx_due_date_expired", 'schedule': timedelta(seconds=30)},
}
app.conf.timezone = 'UTC'
