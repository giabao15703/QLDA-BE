
from apps.users.models import UsersPermission, UserSubstitutionPermission, Buyer, GroupPermission, Supplier, UserDiamondSponsor
from apps.master_data.models import EmailTemplates, EmailTemplatesTranslation
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone

app = Celery('apps', broker=settings.RABBITMQ_URL)

@app.task(name='apps.users.tasks.check_permission_status')
def check_permission_status():
    time_now = timezone.now()
    list_group_permission_id = map(lambda x: x.get('id'), GroupPermission.objects.filter(role=1).values('id'))
    list_user_permissions = map(
        lambda x: x.get('id'), UsersPermission.objects.filter(permission_id__in=list_group_permission_id, status=1).values('id')
    )
    user_permission = UsersPermission.objects.filter(status__in=[1, 4]).exclude(id__in=list_user_permissions)
    for permission in user_permission:
        if permission.valid_to <= time_now and permission.status == 1:
            permission.status = 2
            permission.save()

        if permission.valid_from <= time_now and permission.status == 4:
            permission.status = 1
            permission.save()

    user_substitution_permission = UserSubstitutionPermission.objects.filter(status__in=[1, 4])
    for substitution_permission in user_substitution_permission:
        if substitution_permission.valid_to <= time_now and substitution_permission.status == 1:
            substitution_permission.status = 2
            substitution_permission.save()

        if substitution_permission.valid_from <= time_now and substitution_permission.status == 4:
            substitution_permission.status = 1
            substitution_permission.save()

@app.task(name='apps.users.tasks.check_buyer_status')
def check_buyer_status():
    buyer_list = Buyer.objects.filter(user__status=1)
    for buyer in buyer_list:
        delta_time = (buyer.valid_to - timezone.now()).days
        if delta_time == 30 and buyer.send_mail_30_day is None:
            send_mail_expire(buyer.user, 'AccountExpire30Day')
            buyer.send_mail_30_day = timezone.now()
        if delta_time == 15 and buyer.send_mail_15_day is None:
            send_mail_expire(buyer.user, 'AccountExpire15Day')
            buyer.send_mail_15_day = timezone.now()
        if delta_time == 7 and buyer.send_mail_7_day is None:
            send_mail_expire(buyer.user, 'AccountExpire07Day')
            buyer.send_mail_7_day = timezone.now()
        if buyer.valid_to <= timezone.now():
            buyer.profile_features_id = 1
            if buyer.send_mail_expire is None:
                buyer.send_mail_expire = timezone.now()
                send_mail_expire(buyer.user, 'AccountAlreadyExpired')
        buyer.save()

@app.task(name='apps.users.tasks.check_supplier_status')
def check_supplier_status():
    supplier_list = Supplier.objects.filter(user__status=1)
    for supplier in supplier_list:
        delta_time = (supplier.valid_to - timezone.now()).days
        if delta_time == 30 and supplier.send_mail_30_day is None:
            send_mail_expire(supplier.user, 'AccountExpire30Day')
            supplier.send_mail_30_day = timezone.now()
        if delta_time == 15 and supplier.send_mail_15_day is None:
            send_mail_expire(supplier.user, 'AccountExpire15Day')
            supplier.send_mail_15_day = timezone.now()
        if delta_time == 7 and supplier.send_mail_7_day is None:
            send_mail_expire(supplier.user, 'AccountExpire07Day')
            supplier.send_mail_7_day = timezone.now()
        if supplier.valid_to <= timezone.now():
            supplier.profile_features_id = 1
            if supplier.send_mail_expire is None:
                send_mail_expire(supplier.user, 'AccountAlreadyExpired')
                supplier.send_mail_expire = timezone.now()
        supplier.save()

@app.task(name='apps.users.tasks.check_user_diamond_sponsor_status')
def check_user_diamond_sponsor_status():
    user_diamond_sponsor_list = UserDiamondSponsor.objects.filter(status=1)
    for user_diamond_sponsor in user_diamond_sponsor_list:
        if user_diamond_sponsor.valid_to < timezone.now():
            user_diamond_sponsor.status = 2
            user_diamond_sponsor.is_active = False
            user_diamond_sponsor.save()

@app.task(name='apps.users.tasks.check_user_diamond_sponsor_confirm')
def check_user_diamond_sponsor_confirm():
    user_diamond_sponsor_list = UserDiamondSponsor.objects.filter(user_diamond_sponsor_payment__history__status=6)
    update_list = []
    for user_diamond_sponsor in user_diamond_sponsor_list:
        user_diamond_sponsor.is_confirmed = 3
        update_list.append(user_diamond_sponsor)
    UserDiamondSponsor.objects.bulk_update(update_list, ["is_confirmed"])

def send_mail_expire(user, item_code):
    if user.isBuyer():
        scheme = user.buyer.profile_features
    else:
        scheme = user.supplier.profile_features
    language_code = user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "name": user.full_name,
                "link": "http://192.168.9.94:9001/account",
                "scheme": scheme,
            }
        )
    )
    try:
        send_mail(
            email_template.title, messages, "NextPro <no-reply@nextpro.io>", [user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("Fail mail")
