import math
from apps.users.models import Supplier
from apps.rfx.models import RFXData, RFXSupplier
from apps.rfx.mutation import send_mail_auto_nego_NPDOC9, send_mail_auto_nego_NPDOC10, send_mail_auto_nego_NPDOC11, send_mail_expired_NPDOC5, send_mail_invitation_NPDOC4, send_mail_end_NPDOC20, send_mail_end_NPDOC21
from celery import Celery
from django.conf import settings
from django.db.models import Min
from django.utils import timezone
app = Celery('apps', broker=settings.RABBITMQ_URL)


@app.task(name='apps.rfx.tasks.check_rfx_seat_available')
def check_rfx_seat_available():
    rfxs = RFXData.objects.filter(rfx_suppliers__seat_available=1, rfx_suppliers__is_invited=False)
    for i in rfxs: 
        supplier_joined = RFXSupplier.objects.filter(rfx=i, is_invited=False, is_joined=True).count()
        if supplier_joined >= 7:
            rfx_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=False, is_joined=False)
            for j in rfx_suppliers:
                j.seat_available = 2
                j.quote_submited_status = 6
                j.save()
    return

@app.task(name='apps.rfx.tasks.check_rfx_quote_status')
def check_rfx_quote_status():
    rfxs = RFXData.objects.filter(quote_status=2)
    for i in rfxs:
        is_all_quote_submitted = True
        uninvited_joined_suppliers_count = RFXSupplier.objects.filter(rfx=i, is_invited=False, is_joined=True).count()
        uninvited_joined_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=False, is_joined=True)
        invited_joined_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=True, is_joined=True)

        for j in uninvited_joined_suppliers:
            if j.quote_submited_status != 2:
                is_all_quote_submitted = False 

        for l in invited_joined_suppliers:
            if l.quote_submited_status != 2:
                is_all_quote_submitted = False

        if uninvited_joined_suppliers_count == 7 and (is_all_quote_submitted or i.due_date <= timezone.now()):
            i.quote_status = 1
            i.save()
    return

@app.task(name='apps.rfx.tasks.send_mail_auto_nego')
def send_mail_auto_nego():
    rfxs = RFXData.objects.filter(status=2, auto_negotiation=True)
    for i in rfxs: 
        duration = i.due_date - i.created
        seconds = duration.total_seconds()
        minutes = divmod(seconds, 60)[0]
        interval = round((minutes - 60) / 3)
        send_1 = interval
        send_2 = interval*2
        send_3 = interval*3
        time_send = divmod((timezone.now() - i.created).total_seconds(), 60)[0]
        if time_send == send_1 or time_send == send_2 or time_send == send_3:
            min_price = RFXSupplier.objects.filter(rfx=i, quote_submited_status=2).aggregate(Min('sub_total')).get('sub_total__min')
            rfx_suppliers = RFXSupplier.objects.filter(rfx=i, quote_submited_status=2)
            for j in rfx_suppliers:
                if j.sub_total == min_price:
                    send_mail_auto_nego_NPDOC9("RFX_Auto_Nego_NPDOC9", i, j)
                else:
                    percentage_suggestion = round((j.sub_total/min_price + 0.05 - 1) * 100)
                    if percentage_suggestion > 0 and percentage_suggestion < 5:
                        send_mail_auto_nego_NPDOC10("RFX_Auto_Nego_NPDOC10", i, j, percentage_suggestion)
                    if percentage_suggestion >= 5:
                        send_mail_auto_nego_NPDOC11("RFX_Auto_Nego_NPDOC11", i, j, percentage_suggestion)
     

@app.task(name='apps.rfx.tasks.rfx_send_mail_invitation_NPDOC4')
def rfx_send_mail_invitation_NPDOC4():
    rfxs = RFXData.objects.filter(status=2)
    for i in rfxs:
        duration = timezone.now() - i.created
        view_minutes = i.time_view_minutes 
        view_minutes_2 = view_minutes * 2
        view_minutes_3 = view_minutes * 3
        if duration.days == 0: 
            seconds = duration.seconds
            minutes = math.floor(seconds / 60)
            if minutes == view_minutes:
                rfx_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=False)
                for j in rfx_suppliers:
                    supplier_instance = Supplier.objects.filter(user=j.user).first()
                    if supplier_instance.profile_features.id == 3:
                        send_mail_invitation_NPDOC4("RFX_Invitation_NPDOC4", i, j)
            elif minutes == view_minutes_2:
                rfx_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=False)
                for j in rfx_suppliers:
                    supplier_instance = Supplier.objects.filter(user=j.user).first()
                    if supplier_instance.profile_features.id == 2:
                        send_mail_invitation_NPDOC4("RFX_Invitation_NPDOC4", i, j) 
            elif minutes == view_minutes_3:
                rfx_suppliers = RFXSupplier.objects.filter(rfx=i, is_invited=False)
                for j in rfx_suppliers:
                    supplier_instance = Supplier.objects.filter(user=j.user).first()
                    if supplier_instance.profile_features.id == 1:
                        send_mail_invitation_NPDOC4("RFX_Invitation_NPDOC4", i, j) 

@app.task(name='apps.rfx.tasks.check_rfx_is_full')
def check_rfx_is_full():
    rfxs = RFXData.objects.filter(quote_status=2)
    for i in rfxs:
        invited_suppliers_count = RFXSupplier.objects.filter(rfx=i, is_invited=True).count()
        joined_suppliers_count = RFXSupplier.objects.filter(rfx=i, quote_submited_status=2).count()
        if invited_suppliers_count == 3:
            if joined_suppliers_count == 10:
                i.is_full = True 
        elif invited_suppliers_count == 2:
            if joined_suppliers_count == 9:
                i.is_full = True
        elif invited_suppliers_count == 1:
            if joined_suppliers_count == 8:
                i.is_full = True
        else:
            if joined_suppliers_count == 7:
                i.is_full = True
        i.save(update_fields=['is_full'])

@app.task(name='apps.rfx.tasks.check_rfx_due_date_expired')
def check_rfx_due_date_expired():
    rfxs = RFXData.objects.filter(status=2)
    for i in rfxs:
        rfx_suppliers = RFXSupplier.objects.filter(rfx=i)
        if i.due_date <= timezone.now():
            for j in rfx_suppliers:
                if j.quote_submited_status == 1:
                    j.quote_submited_status = 6
                    j.save(update_fields=['quote_submited_status'])
                if j.quote_submited_status == 2:
                    if i.auto_negotiation == True:
                        send_mail_end_NPDOC21("RFX_End_NPDOC21", i, j) 
            if i.auto_negotiation == True: 
                send_mail_end_NPDOC20("RFX_End_NPDOC20", i)
            else:
                send_mail_expired_NPDOC5("RFX_Expired_NPDOC5", i)
            i.status = 3
            i.save(update_fields=['status'])
    return