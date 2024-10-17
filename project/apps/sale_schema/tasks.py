from celery import Celery
from apps.sale_schema.models import OurPartner
from django.utils import timezone
from django.conf import settings


app = Celery('apps', broker=settings.RABBITMQ_URL)

@app.task(name='apps.sale_schema.tasks.check_our_partner_status')
def check_our_partner_status():
    our_partner_list = OurPartner.objects.filter(status=True)
    for our_partner in our_partner_list:
        if our_partner.valid_to < timezone.now():
            our_partner.status = False
            our_partner.save()