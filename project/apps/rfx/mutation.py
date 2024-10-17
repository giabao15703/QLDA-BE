import graphene
import pytz

from django.core.mail import send_mail, EmailMessage
from django.db import transaction
from django.db.models import Min
from django.utils import timezone
from django.template import Template, Context
from graphene_file_upload.scalars import Upload

from apps.core import Error, get_full_company_address
from apps.rfx.error_code import RFXError
from apps.users.models import User, Supplier
from apps.sale_schema.models import ProfileFeaturesBuyer
from apps.rfx.models import (
    RFXData,
    RFXItem,
    RFXAttachment,
    RFXSupplier,
    RFXItemSupplier,
    RFXAward
)
from apps.rfx.schema import (
    RFXNode,
    RFXSupplierNode,
    GetToken,
)

from apps.master_data.models import (
    EmailTemplates,
    Category,
    Currency,
    ContractType,
    PaymentTerm,
    DeliveryTerm,
    UnitofMeasure,
    EmailTemplatesTranslation,
    Country,
    CountryState
)
from apps.rfx.views import generate_pdf


def send_mail_auto_nego_NPDOC9(item_code, rfx, rfx_supplier):
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "supplier_user_name": rfx_supplier.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "buyer_name": rfx.user.buyer.company_full_name,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx_supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_auto_nego_NPDOC10(item_code, rfx, rfx_supplier, percentage):
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "supplier_user_name": rfx_supplier.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "buyer_name": rfx.user.buyer.company_full_name,
                "percentage": percentage,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx_supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_auto_nego_NPDOC11(item_code, rfx, rfx_supplier, percentage):
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    tz = pytz.timezone(rfx_supplier.user.local_time)
    start_time = rfx.due_date.replace(tzinfo=pytz.utc).astimezone(tz)
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "supplier_user_name": rfx_supplier.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "buyer_name": rfx.user.buyer.company_full_name,
                "percentage": percentage,
                "due_date": start_time.strftime('%Y/%m/%d'),
                "time_value": start_time.strftime('%H:%M'),
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx_supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_invitation_NPDOC3(item_code, rfx, rfx_supplier):
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    tz = pytz.timezone(rfx_supplier.user.local_time)
    start_time = rfx.due_date.replace(tzinfo=pytz.utc).astimezone(tz)
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "supplier_user_name": rfx_supplier.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "buyer_name": rfx.user.buyer.company_full_name,
                "due_date": start_time.strftime('%Y/%m/%d'),
                "time_value": start_time.strftime('%H:%M'),
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title,
            messages,
            "NextPro <no-reply@nextpro.io>",
            [rfx_supplier.user.email],
            html_message=messages,
            fail_silently=True,
        )
    except:
        print("Send email NPDOC3 failed")


def send_mail_invitation_NPDOC4(item_code, rfx, rfx_supplier):
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    tz = pytz.timezone(rfx_supplier.user.local_time)
    start_time = rfx.due_date.replace(tzinfo=pytz.utc).astimezone(tz)
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "supplier_user_name": rfx_supplier.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "buyer_name": rfx.user.buyer.company_full_name,
                "due_date": start_time.strftime('%Y/%m/%d'),
                "time_value": start_time.strftime('%H:%M'),
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx_supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_expired_NPDOC5(item_code, rfx):
    join_amount = RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2).count()
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "buyer_user_name": rfx.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "number": join_amount,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_cancel_NPDOC17(item_code, rfx):
    buyer_profile = ProfileFeaturesBuyer.objects.filter(id=rfx.user.buyer.profile_features.id).first()
    max = buyer_profile.no_eauction_year
    total = RFXData.objects.filter(user=rfx.user, status=8).count()
    min = max - total
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "buyer_user_name": rfx.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "max_cancellation": max,
                "remain_cancellation": min,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_PO_NPDOC14(item_code, rfx, supplier):
    language_code = rfx.user.language.item_code
    user_buyer = rfx.user
    user_supplier = supplier.user
    now = timezone.now().astimezone(tz=pytz.timezone("Etc/GMT-7"))
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code__iexact=language_code)
    if not email_template.exists():
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    if email_template is None:
        print("Send mail NPDOC14 failed")
        return
    try:
        messages = Template(email_template.content).render(
            Context(
                {
                    "image": "https://api.nextpro.io/static/logo_mail.png",
                    "supplier_user_name": user_supplier.full_name,
                    "buyer_company_long_name": user_buyer.buyer.company_full_name,
                    "item_code": rfx.item_code,
                    "title": rfx.title,
                }
            )
        )
        title = email_template.title
        email = EmailMessage(
            title,
            messages,
            'NextPro <no-reply@nextpro.io>',
            [user_supplier.email],
            headers={'Reply-To': 'NextPro <no-reply@nextpro.io>'},
            cc=[user_buyer.email],
        )
        email.content_subtype = "html"

        rfx_award_list = rfx.rfx_awards.filter(
            user=user_supplier
        ).select_related("rfx_item")
        item_list = []
        sub_total_amount = 0
        vat_amount = 0
        for rfx_award in rfx_award_list:
            rfx_item = rfx_award.rfx_item
            rfx_item_supplier = RFXItemSupplier.objects.filter(
                rfx_supplier__user=user_supplier,
                rfx_item=rfx_item
            ).order_by("-order").first()
            if rfx_item.unit:
                if rfx_item.unit.translations.filter(language_code=language_code).exists():
                    unit_name = rfx_item.unit.translations.filter(language_code=language_code).first().name
                else:
                    unit_name = rfx_item.unit.name
            else:
                unit_name = ''
            if rfx_item_supplier.vat_tax:
                vat_tax = rfx_item_supplier.vat_tax
            else:
                vat_tax = 0
            item_total_amount = rfx_item_supplier.unit_price * rfx_item.quantity * rfx_item_supplier.percentage / 100
            sub_total_amount += item_total_amount
            vat_amount += item_total_amount * vat_tax / 100
            unit_price = rfx_item_supplier.unit_price
            if unit_price == round(unit_price):
                unit_price = round(unit_price)
            quantity = rfx_item.quantity * rfx_item_supplier.percentage / 100
            if quantity == round(quantity):
                quantity = round(quantity)
            item_list.append(
                {
                    'name': rfx_item.name,
                    'part_number': rfx_item.part_number,
                    'delivery_from': rfx_item.delivery_from.strftime("%d/%m/%Y") if rfx_item.delivery_from else '',
                    'delivery_to': rfx_item.delivery_to.strftime("%d/%m/%Y") if rfx_item.delivery_to else '',
                    'quantity': "{:,}".format(quantity),
                    'unit': unit_name,
                    'unit_price': "{:,}".format(unit_price),
                }
            )

        if rfx.currency:
            currency = rfx.currency.item_code
        else:
            currency = ''

        if rfx.payment_term:
            if rfx.payment_term.translations.filter(language_code=language_code).exists():
                payment_term = rfx.payment_term.translations.filter(language_code=language_code).first().name
            else:
                payment_term = rfx.payment_term.name
        else:
            payment_term = ''

        if rfx.delivery_term:
            if rfx.delivery_term.translations.filter(language_code=language_code).exists():
                delivery_term = rfx.delivery_term.translations.filter(language_code=language_code).first().name
            else:
                delivery_term = rfx.delivery_term.name
        else:
            delivery_term = ''

        if language_code == "vi":
            if rfx.terms_and_conditions:
                terms_and_conditions = "Áp dụng"
            else:
                terms_and_conditions = "Không áp dụng"
        else:
            if rfx.terms_and_conditions:
                terms_and_conditions = "Apply"
            else:
                terms_and_conditions = "Do not apply"
        if sub_total_amount == round(sub_total_amount):
            sub_total_amount = round(sub_total_amount)
        if vat_amount == round(vat_amount):
            vat_amount = round(vat_amount)
        data = {
            'item_code': rfx.item_code,
            'date': rfx.due_date.strftime('%d-%m-%Y') if rfx.due_date else "",
            'item_list': item_list,
            'rfx_awarded_date': now.strftime("%d/%m/%Y"),
            'currency': currency,
            'payment_term': payment_term,
            'delivery_term': delivery_term,
            'delivery_address': rfx.delivery_address if rfx.delivery_address else "",
            'terms_and_conditions': terms_and_conditions,
            'sub_total_amount': "{:,}".format(sub_total_amount),
            'vat_amount': "{:,}".format(vat_amount),
            'grand_total_amount': "{:,}".format(sub_total_amount + vat_amount),
        }
        if user_buyer.isBuyer():
            buyer = user_buyer.buyer
            data['buyer_code'] = user_buyer.username
            data['buyer_company_name'] = buyer.company_full_name
            if buyer.company_country.translations.filter(language_code=language_code).exists():
                buyer_company_country_name = buyer.company_country.translations.filter(language_code=language_code).first().name
            else:
                buyer_company_country_name = buyer.company_country.name
            buyer_company_city = buyer.company_city
            if buyer.company_country_state.state_code != "UNKNOWN":
                if buyer.company_country_state.translations.filter(language_code=language_code).exists():
                    buyer_company_city = buyer.company_country_state.translations.filter(language_code=language_code).first().name
                else:
                    buyer_company_city = buyer.company_country_state.name
            data['buyer_company_address'] = get_full_company_address(
                buyer.company_address,
                buyer_company_city,
                buyer_company_country_name
            )
            data['buyer_contact_name'] = user_buyer.full_name
            data['buyer_phone'] = buyer.phone
            data['buyer_email'] = user_buyer.email
            data['buyer_company_tax'] = buyer.company_tax
            data['buyer_company_country'] = buyer.company_country.name
            data['buyer_company_state'] = buyer.company_country_state.name
        if user_supplier.isSupplier():
            supplier = user_supplier.supplier
            data['supplier_code'] = user_supplier.username
            data['supplier_company_name'] = supplier.company_full_name
            if supplier.company_country.translations.filter(language_code=language_code).exists():
                supplier_company_country_name = supplier.company_country.translations.filter(language_code=language_code).first().name
            else:
                supplier_company_country_name = supplier.company_country.name
            supplier_company_city = supplier.company_city
            if supplier.company_country_state.state_code != "UNKNOWN":
                if supplier.company_country_state.translations.filter(language_code=language_code).exists():
                    supplier_company_city = supplier.company_country_state.translations.filter(language_code=language_code).first().name
                else:
                    supplier_company_city = supplier.company_country_state.name
            data['supplier_company_address'] = get_full_company_address(
                supplier.company_address,
                supplier_company_city,
                supplier_company_country_name
            )
            data['supplier_name'] = user_supplier.full_name
            data['supplier_email'] = user_supplier.email
            data['supplier_phone'] = supplier.phone
            data['beneficiary_name'] = supplier.beneficiary_name
            data['bank_name'] = supplier.bank_name
            data['bank_account_number'] = supplier.bank_account_number

        if language_code == "vi":
            file_purchase_order_template = "purchase_order_vi.html"
            file_purchase_order_confirmation_template = "purchase_order_confirmation_vi.html"
        else:
            file_purchase_order_template = "purchase_order.html"
            file_purchase_order_confirmation_template = "purchase_order_confirmation.html"
        generate_pdf(data, file_purchase_order_template, "purchase_order.pdf", "{}/{}/supplier_{}".format(user_buyer.id, rfx.item_code, user_supplier.id))
        generate_pdf(data, file_purchase_order_confirmation_template, "purchase_order_confirmation.pdf", "{}/{}/supplier_{}".format(user_buyer.id, rfx.item_code, user_supplier.id))
        email.attach_file(f'''./media/{user_buyer.id}/{rfx.item_code}/supplier_{user_supplier.id}/purchase_order.pdf''')
        email.attach_file(f'''./media/{user_buyer.id}/{rfx.item_code}/supplier_{user_supplier.id}/purchase_order_confirmation.pdf''')
        email.send(fail_silently=False)
        return
    except Exception as error:
        print(error)
        print("Send mail NPDOC14 failed")
        return


def send_mail_end_NPDOC20(item_code, rfx):
    join_amount = RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2).count()
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template.exists():
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "buyer_user_name": rfx.user.full_name,
                "item_code": rfx.item_code,
                "title": rfx.title,
                "number_submitted": join_amount,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_end_NPDOC21(item_code, rfx, rfx_supplier):
    join_amount = RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2, user=rfx_supplier.user).count()
    language_code = rfx.user.language.item_code
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template:
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    messages = Template(email_template.content).render(
        Context(
            {
                "image": "https://api.nextpro.io/static/logo_mail.png",
                "item_code": rfx.item_code,
                "supplier_user_name": rfx_supplier.user.full_name,
                "title": rfx.title,
                "number_submitted": join_amount,
                "buyer_company_name": rfx.user.buyer.company_full_name,
            }
        )
    )
    title = email_template.title

    try:
        send_mail(
            title, messages, "NextPro <no-reply@nextpro.io>", [rfx_supplier.user.email], html_message=messages, fail_silently=True,
        )
    except:
        print("fail mail")


def send_mail_PO_NPDOC22(item_code, rfx):
    user_buyer = rfx.user
    user_supplier = supplier.user
    language_code = user_buyer.language.item_code
    now = timezone.now().astimezone(tz=pytz.timezone("Etc/GMT-7"))
    email_template = EmailTemplatesTranslation.objects.filter(email_templates__item_code=item_code, language_code=language_code)
    if not email_template.exists():
        email_template = EmailTemplates.objects.filter(item_code=item_code)
    email_template = email_template.first()
    if email_template is not None:
        try:
            messages = Template(email_template.content).render(
                Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "buyer_name": user_buyer.full_name,
                        "buyer_company_long_name": user_buyer.buyer.company_full_name,
                        "item_code": rfx.item_code,
                        "title": rfx.title,
                    }
                )
            )
            title = email_template.title
            email = EmailMessage(
                title,
                messages,
                'NextPro <no-reply@nextpro.io>',
                [user_buyer.email],
                headers={'Reply-To': 'NextPro <no-reply@nextpro.io>'},
            )
            email.content_subtype = "html"
            items = rfx.items.all()
            item_list = []
            sub_total_amount = 0
            for i in items:
                if i.unit:
                    if i.unit.translations.filter(language_code=language_code).exists():
                        unit_name = i.unit.translations.filter(language_code=language_code).first().name
                    else:
                        unit_name = i.unit.name
                else:
                    unit_name = ''
                item_list.append(
                    {
                        'name': i.name,
                        'part_number': i.part_number,
                        'delivery_from': i.delivery_from.strftime("%d/%m/%Y") if i.delivery_from else '',
                        'delivery_to': i.delivery_to.strftime("%d/%m/%Y") if i.delivery_to else '',
                        'quantity': i.quantity,
                        'unit': unit_name,
                        'unit_price': i.unit_price if i.unit_price else 0,
                    }
                )
                if i.unit_price:
                    sub_total_amount += i.quantity * i.unit_price
            if rfx.currency:
                currency = rfx.currency.item_code
            else:
                currency = ''

            if rfx.payment_term:
                if rfx.payment_term.translations.filter(language_code=language_code).exists():
                    payment_term = rfx.payment_term.translations.filter(language_code=language_code).first().name
                else:
                    payment_term = rfx.payment_term.name
            else:
                payment_term = ''

            if rfx.delivery_term:
                if rfx.delivery_term.translations.filter(language_code=language_code).exists():
                    delivery_term = rfx.delivery_term.translations.filter(language_code=language_code).first().name
                else:
                    delivery_term = rfx.delivery_term.name
            else:
                delivery_term = ''

            if language_code == "vi":
                if rfx.terms_and_conditions:
                    terms_and_conditions = "Áp dụng"
                else:
                    terms_and_conditions = "Không áp dụng"
            else:
                if rfx.terms_and_conditions:
                    terms_and_conditions = "Apply"
                else:
                    terms_and_conditions = "Do not apply"

            data = {
                'item_code': rfx.item_code,
                'date': rfx.due_date.strftime('%d-%m-%Y'),
                'item_list': item_list,
                'rfx_awarded_date': now.strftime("%d/%m/%Y"),
                'currency': currency,
                'payment_term': payment_term,
                'delivery_term': delivery_term,
                'delivery_address': rfx.delivery_address,
                'terms_and_conditions': terms_and_conditions,
                'sub_total_amount': sub_total_amount
            }
            if user_buyer.isBuyer():
                buyer = user_buyer.buyer
                data['buyer_code'] = user_buyer.username
                data['buyer_company_name'] = buyer.company_full_name
                if buyer.company_country.translations.filter(language_code=language_code).exists():
                    buyer_company_country_name = buyer.company_country.translations.filter(language_code=language_code).first().name
                else:
                    buyer_company_country_name = buyer.company_country.name
                buyer_company_city = buyer.company_city
                if buyer.company_country_state.state_code != "UNKNOWN":
                    if buyer.company_country_state.translations.filter(language_code=language_code).exists():
                        buyer_company_city = buyer.company_country_state.translations.filter(language_code=language_code).first().name
                    else:
                        buyer_company_city = buyer.company_country_state.name
                data['buyer_company_address'] = get_full_company_address(
                    buyer.company_address,
                    buyer_company_city,
                    buyer_company_country_name
                )
                data['buyer_contact_name'] = user_buyer.full_name
                data['buyer_phone'] = buyer.phone
                data['buyer_email'] = user_buyer.email
            if user_supplier.isSupplier():
                supplier = user_supplier.supplier
                data['supplier_code'] = user_supplier.username
                data['supplier_company_name'] = supplier.company_full_name
                if supplier.company_country.translations.filter(language_code=language_code).exists():
                    supplier_company_country_name = supplier.company_country.translations.filter(language_code=language_code).first().name
                else:
                    supplier_company_country_name = supplier.company_country.name
                supplier_company_city = supplier.company_city
                if supplier.company_country_state.state_code != "UNKNOWN":
                    if supplier.company_country_state.filter(language_code=language_code).exists():
                        supplier_company_city = supplier.company_country_state.filter(language_code=language_code).first().name
                    else:
                        supplier_company_city = supplier.company_country_state.name
                data['supplier_company_address'] = get_full_company_address(
                    supplier.company_address,
                    supplier_company_city,
                    supplier_company_country_name
                )
                data['supplier_name'] = user_supplier.full_name
                data['supplier_email'] = user_supplier.email
                data['supplier_phone'] = supplier.phone

            for item in data['item_list']:
                if item['unit_price'] is not None:
                    item['unit_price'] = '{:20,.0f}'.format(item['unit_price'])

            generate_pdf(data, "purchase_order.html", "purchase_order.pdf", "{}/{}".format(rfx.user.id, rfx.item_code))
            email.send(fail_silently=True)
        except Exception as error:
            print(error)
            print("Send mail NPDOC22 failed")
    else:
        print("Send mail NPDOC22 failed")


class RFXItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    part_number = graphene.String()
    quantity = graphene.Int(required=True)
    unit = graphene.String(required=True)
    unit_price = graphene.Float()
    total_amount = graphene.Float()
    delivery_from = graphene.Date()
    delivery_to = graphene.Date()


class RFXInput(graphene.InputObjectType):
    rfx_type = graphene.Int(required=True)
    title = graphene.String(required=True)
    budget = graphene.Float(required=True)
    category = graphene.String(required=True)
    currency = graphene.String(required=True)
    due_date = graphene.DateTime(required=True)
    contract_type = graphene.String(required=True)
    from_date = graphene.Date(reqired=True)
    to_date = graphene.Date(reqired=True)
    payment_term = graphene.String(reqired=True)
    delivery_term = graphene.String(reqired=True)
    delivery_address = graphene.String(reqired=True)
    terms_and_conditions = graphene.Boolean()
    auto_negotiation = graphene.Boolean()
    other_requirement = graphene.String()
    note_for_supplier = graphene.String()
    status = graphene.Int(required=True)
    split_order = graphene.Int(required=True)
    rfx_next_round = graphene.Int()
    rfx_suppliers = graphene.List(graphene.Int)
    rfx_items = graphene.List(RFXItemInput, required=True)
    internal_attachments = graphene.List(Upload)
    external_attachments = graphene.List(Upload)
    attachments_deleted = graphene.List(graphene.Int)
    rfx_suppliers_deleted = graphene.List(graphene.Int)
    rfx_suppliers_nego = graphene.List(graphene.Int)
    country = graphene.String(required=False)
    country_state = graphene.String(required=False)


class RFXCreate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    rfx = graphene.Field(RFXNode)

    class Arguments:
        input = RFXInput(required=True)

    def mutate(root, info, input):
        try:
            error = None
            token = GetToken.getToken(info)
            user = token.user
            if user.isBuyer():
                if 'rfx_suppliers' in input and len(input.rfx_suppliers) > 3:
                    error = Error(code="RFX_03", message=RFXError.RFX_03)
                    transaction.set_rollback(True)
                    return RFXCreate(status=False, error=error)

                rfx_count = RFXData.objects.filter(rfx_next_round__isnull=True).count() + 1
                item_code = '50' + str(rfx_count).zfill(4)
                if input.rfx_next_round:
                    rfx = RFXData.objects.filter(id=input.rfx_next_round).first()
                    RFXSupplier.objects.filter(rfx_id=input.rfx_next_round).update(quote_submited_status=2)
                    item_code = float("{0:.2f}".format(float(rfx.item_code) + 0.1))
                input['item_code'] = item_code
                input['max_supplier'] = 10
                input['user'] = user
                rfx = RFXData()
                for key, values in input.items():
                    if key in [f.name for f in RFXData._meta.get_fields()]:
                        if key == "category":
                            if values == '':
                                values = None
                            else:
                                values = Category.objects.get(id=values)
                        elif key == "currency":
                            values = Currency.objects.get(id=values)
                        elif key == "contract_type":
                            values = ContractType.objects.get(id=values)
                        elif key == "payment_term":
                            values = PaymentTerm.objects.get(id=values)
                        elif key == "delivery_term":
                            values = DeliveryTerm.objects.get(id=values)
                        elif key == "rfx_next_round":
                            values = RFXData.objects.get(id=values)
                        elif key == "rfx_suppliers":
                            continue
                        elif key == "internal_attachments":
                            continue
                        elif key == "external_attachments":
                            continue
                        elif key == "country":
                            values = Country.objects.get(id=values)
                        elif key == "country_state":
                            values = CountryState.objects.get(id=values)

                        setattr(rfx, key, values)
                rfx.save()

                if 'rfx_items' in input and input.rfx_items is not None:
                    for i in input.rfx_items:
                        unit = UnitofMeasure.objects.filter(id=i.unit).first()
                        RFXItem.objects.create(
                            rfx=rfx,
                            name=i.name,
                            part_number=i.part_number,
                            quantity=i.quantity,
                            unit=unit,
                            unit_price=i.unit_price,
                            total_amount=i.total_amount,
                            delivery_from=i.delivery_from,
                            delivery_to=i.delivery_to,
                        )

                if 'internal_attachments' in input and input.internal_attachments is not None:
                    for i in input.internal_attachments:
                        rfx_attachment = RFXAttachment(
                            rfx=rfx,
                            attachment=i,
                            attachment_type=1,
                            upload_by=1,
                        )
                        rfx_attachment.save()

                if 'external_attachments' in input and input.external_attachments is not None:
                    for i in input.external_attachments:
                        rfx_attachment = RFXAttachment(
                            rfx=rfx,
                            attachment=i,
                            attachment_type=2,
                            upload_by=1,
                        )
                        rfx_attachment.save()

                if 'rfx_suppliers' in input and input.rfx_suppliers is not None:
                    for i in input.rfx_suppliers:
                        user_instance = User.objects.filter(supplier__id=i).first()
                        rfx_supplier_instance = RFXSupplier(
                            user=user_instance,
                            rfx=rfx,
                            quote_submited_status=1,
                            is_invited=True,
                            is_joined=True,
                        )
                        rfx_supplier_instance.save()
                        if input.status == 2:
                            send_mail_invitation_NPDOC3("RFX_Invitation_NPDOC3", rfx, rfx_supplier_instance)

                if input.rfx_next_round is None:
                    if rfx.category:
                        suppliers = Supplier.objects.filter(suppliercategory__category_id__id=rfx.category.id).exclude(id__in=input.rfx_suppliers)
                        if suppliers is not None and len(suppliers) > 0:
                            for i in suppliers:
                                rfx_supplier = RFXSupplier(
                                    user=i.user,
                                    rfx=rfx,
                                    quote_submited_status=1,
                                    is_invited=False,
                                    is_joined=False,
                                )
                                rfx_supplier.save()
                else:
                    if 'attachments_deleted' in input and input.attachments_deleted is not None:
                        rfx_attachments = RFXAttachment.objects.filter(rfx_id=input.rfx_next_round).exclude(id__in=input.attachments_deleted)
                    else:
                        rfx_attachments = RFXAttachment.objects.filter(rfx_id=input.rfx_next_round)
                    for i in rfx_attachments:
                        rfx_attachment = RFXAttachment(
                            rfx=rfx,
                            attachment=i.attachment,
                            attachment_type=i.attachment_type,
                            upload_by=i.upload_by,
                        )
                        rfx_attachment.save()

                    if 'rfx_suppliers_nego' in input and input.rfx_suppliers_nego is not None:
                        for i in input.rfx_suppliers_nego:
                            user_instance = User.objects.filter(supplier__id=i).first()
                            rfx_supplier_instance = RFXSupplier(
                                user=user_instance,
                                rfx=rfx,
                                quote_submited_status=1,
                                is_invited=True,
                                is_joined=True,
                            )
                            rfx_supplier_instance.save()

                return RFXCreate(rfx=rfx, status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                transaction.set_rollback(True)
                return RFXCreate(status=False, error=error)
        except Exception as err:
            transaction.set_rollback(True)
            if error is None:
                error = err
            return RFXCreate(status=False, error=error)


class RFXUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    rfx = graphene.Field(RFXNode)

    class Arguments:
        id = graphene.String(required=True)
        input = RFXInput(required=True)

    def mutate(root, info, input, id):
        try:
            error = None
            token = GetToken.getToken(info)
            user = token.user
            if user.isBuyer():
                rfx_instance = RFXData.objects.filter(id=id).first()
                pre_category_id = rfx_instance.category_id
                if '.' not in rfx_instance.item_code:
                    if 'rfx_suppliers' in input and len(input.rfx_suppliers) > 3:
                        error = Error(code="RFX_03", message=RFXError.RFX_03)
                        return RFXUpdate(status=False, error=error)
                input["user"] = user
                if input.status == 2:
                    input["created"] = timezone.now()
                for key, values in input.items():
                    if key in [f.name for f in RFXData._meta.get_fields()]:
                        if key == "category":
                            if values == '':
                                values = None
                            else:
                                values = Category.objects.get(id=values)
                        elif key == "currency":
                            values = Currency.objects.get(id=values)
                        elif key == "contract_type":
                            values = ContractType.objects.get(id=values)
                        elif key == "payment_term":
                            values = PaymentTerm.objects.get(id=values)
                        elif key == "delivery_term":
                            values = DeliveryTerm.objects.get(id=values)
                        elif key == "rfx_next_round":
                            values = RFXData.objects.get(id=values)
                        elif key == "country":
                            values = Country.objects.get(id=values)
                        elif key == "country_state":
                            values = CountryState.objects.get(id=values)
                        elif key == "rfx_suppliers":
                            continue
                        elif key == "internal_attachments":
                            continue
                        elif key == "external_attachments":
                            continue

                        setattr(rfx_instance, key, values)
                rfx_instance.save()
                subs_category_id = rfx_instance.category_id

                if 'rfx_items' in input and input.rfx_items is not None:
                    RFXItem.objects.filter(rfx=rfx_instance).delete()
                    for i in input.rfx_items:
                        unit = UnitofMeasure.objects.filter(id=i.unit).first()
                        RFXItem.objects.create(
                            rfx=rfx_instance,
                            name=i.name,
                            part_number=i.part_number,
                            quantity=i.quantity,
                            unit=unit,
                            unit_price=i.unit_price,
                            total_amount=i.total_amount,
                            delivery_from=i.delivery_from,
                            delivery_to=i.delivery_to,
                        )

                if 'attachments_deleted' in input and input.attachments_deleted is not None:
                    for i in input.attachments_deleted:
                        RFXAttachment.objects.get(pk=i).delete()

                if 'internal_attachments' in input and input.internal_attachments is not None:
                    for i in input.internal_attachments:
                        rfx_attachment = RFXAttachment(
                            rfx=rfx_instance,
                            attachment=i,
                            attachment_type=1,
                            upload_by=1,
                        )
                        rfx_attachment.save()

                if 'external_attachments' in input and input.external_attachments is not None:
                    for i in input.external_attachments:
                        rfx_attachment = RFXAttachment(
                            rfx=rfx_instance,
                            attachment=i,
                            attachment_type=2,
                            upload_by=1,
                        )
                        rfx_attachment.save()

                if 'rfx_suppliers_deleted' in input and len(input.rfx_suppliers_deleted) > 0:
                    for i in input.rfx_suppliers_deleted:
                        user = User.objects.filter(supplier__id=i).first()
                        rfx_supplier_in = RFXSupplier.objects.filter(user=user, rfx=rfx_instance, is_invited=True).first()
                        supplier_in = Supplier.objects.filter(user=user, suppliercategory__category_id__id=rfx_instance.category.id).first()
                        if supplier_in is not None:
                            rfx_supplier_in.is_invited = False
                            rfx_supplier_in.is_joined = False
                            rfx_supplier_in.save()
                        else:
                            rfx_supplier_in.delete()

                if 'rfx_suppliers' in input and input.rfx_suppliers is not None:
                    for i in input.rfx_suppliers:
                        user_instance = User.objects.filter(supplier__id=i).first()
                        RFXSupplier.objects.filter(rfx=rfx_instance, is_invited=False, user=user_instance).delete()

                    for i in input.rfx_suppliers:
                        user_instane = User.objects.filter(supplier__id=i).first()
                        rfx_supplier_instance = RFXSupplier(
                            user=user_instane,
                            rfx=rfx_instance,
                            quote_submited_status=1,
                            is_invited=True,
                            is_joined=True,
                        )
                        rfx_supplier_instance.save()

                    rfx_supplier_count = RFXSupplier.objects.filter(rfx=rfx_instance, is_invited=True).count()
                    if '.' not in rfx_instance.item_code:
                        if rfx_supplier_count > 3:
                            error = Error(code="RFX_03", message=RFXError.RFX_03)
                            transaction.set_rollback(True)
                            return RFXUpdate(status=False, error=error)

                if pre_category_id != subs_category_id:
                    RFXSupplier.objects.filter(rfx=rfx_instance, is_invited=False).delete()
                    users = map(
                        lambda x: x.get('user'), RFXSupplier.objects.filter(rfx=rfx_instance, is_invited=True).values('user')
                    )
                    supplier_ids = []
                    for i in users:
                        user = User.objects.filter(id=i).first()
                        supplier_ids.append(user.supplier.id)
                    suppliers = Supplier.objects.filter(suppliercategory__category_id__id=rfx_instance.category.id).exclude(id__in=supplier_ids)
                    if suppliers is not None and len(suppliers) > 0:
                        for i in suppliers:
                            rfx_supplier = RFXSupplier(
                                user=i.user,
                                rfx=rfx_instance,
                                quote_submited_status=1,
                                is_invited=False,
                                is_joined=False,
                            )
                            rfx_supplier.save()
                if input.status == 2:
                    rfx_supplier_instances = RFXSupplier.objects.filter(rfx=rfx_instance, is_invited=True)
                    for i in rfx_supplier_instances:
                        send_mail_invitation_NPDOC3("RFX_Invitation_NPDOC3", rfx_instance, i)

                return RFXUpdate(rfx=rfx_instance, status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXUpdate(status=False, error=error)
        except Exception as err:
            print(err)
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXUpdate(status=False, error=error)


class RFXStatusUpdateInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    status = graphene.Int(required=True)


class RFXStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        input = RFXStatusUpdateInput(required=True)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isBuyer():
                rfx_instance = RFXData.objects.filter(id=input.id).first()
                rfx_instance.status = input.status
                rfx_instance.save()
                if input.status == 8:
                    rfx_suppliers = RFXSupplier.objects.filter(rfx=rfx_instance)
                    for rfx_supplier in rfx_suppliers:
                        rfx_supplier.quote_submited_status = 6
                        rfx_supplier.save()
                    send_mail_cancel_NPDOC17("RFX_Cancel_NPDOC17", rfx_instance)
                return RFXStatusUpdate(status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXStatusUpdate(error=error, status=False)
        except:
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXStatusUpdate(error=error, status=False)


class RFXSupplierQuoteSubmitedStatusUpdateInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    quote_submited_status = graphene.Int(required=True)


class RFXSupplierQuoteSubmitedStatusUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        list_quote = graphene.List(RFXSupplierQuoteSubmitedStatusUpdateInput, required=True)

    def mutate(root, info, list_quote):

        try:
            token = GetToken.getToken(info)
            user = token.user
        except:
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXSupplierQuoteSubmitedStatusUpdate(error=error, status=False)

        if user.isSupplier() or user.isBuyer():
            for i in list_quote:
                rfx_supplier_instance = RFXSupplier.objects.filter(id=i.id).first()
                rfx_supplier_instance.quote_submited_status = i.quote_submited_status
                rfx_supplier_instance.save()
            return RFXSupplierQuoteSubmitedStatusUpdate(status=True)
        else:
            error = Error(code="RFX_01", message=RFXError.RFX_01)
            return RFXSupplierQuoteSubmitedStatusUpdate(error=error, status=False)


class RFXIsJoinedUpdateInput(graphene.InputObjectType):
    rfx_id = graphene.String(required=True)
    is_joined = graphene.Boolean(required=True)


class RFXIsJoinedUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)
    rfx_supplier = graphene.Field(RFXSupplierNode)

    class Arguments:
        input = RFXIsJoinedUpdateInput()

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isSupplier():
                rfx = RFXData.objects.filter(id=input.rfx_id).first()
                if rfx.status == 3:
                    error = Error(code="RFX_07", message=RFXError.RFX_07)
                    return RFXIsJoinedUpdate(error=error, status=False)
                rfx_supplier_instance = RFXSupplier.objects.filter(user=user, rfx_id=input.rfx_id).first()
                rfx_supplier_count = RFXSupplier.objects.filter(rfx_id=input.rfx_id, is_invited=False, is_joined=True).count()
                if rfx_supplier_count < 7:
                    rfx_supplier_instance.is_joined = input.is_joined
                    rfx_supplier_instance.save()
                    return RFXIsJoinedUpdate(status=True, rfx_supplier=rfx_supplier_instance)
                else:
                    error = Error(code="RFX_05", message=RFXError.RFX_05)
                    return RFXIsJoinedUpdate(error=error, status=False)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXIsJoinedUpdate(error=error, status=False)
        except:
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXIsJoinedUpdate(error=error, status=False)


class RFXAwardSupplierInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    percentage = graphene.Float(required=True)
    price = graphene.Float(required=True)


class RFXAwardInput(graphene.InputObjectType):
    rfx_item_id = graphene.String(required=True)
    suppliers = graphene.List(RFXAwardSupplierInput, required=True)


class RFXAwardCreate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        items = graphene.List(RFXAwardInput)
        rfx_id = graphene.String(required=True)

    def mutate(root, info, rfx_id, items):
        try:
            token = GetToken.getToken(info)
            user = token.user

            if not user.isBuyer():
                transaction.set_rollback(True)
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXAwardCreate(error=error, status=False)

            set_supplier_ids = set()
            rfx = RFXData.objects.filter(id=rfx_id).first()
            rfx_next_round = RFXData.objects.filter(rfx_next_round=rfx).exists()
            if rfx_next_round:
                error = Error(code="RFX_09", message=RFXError.RFX_09)
                return RFXAwardCreate(error=error, status=False)
            if rfx.split_order == 1 and any(len(i.suppliers) == 0 for i in items):
                error = Error(code="RFX_18", message=RFXError.RFX_18)
                return RFXAwardCreate(error=error, status=False)

            if rfx.split_order == 2:
                for i in items:
                    rfx_item = RFXItem.objects.filter(id=i.rfx_item_id).first()
                    total_percentage = 0
                    for j in i.suppliers:
                        total_percentage += j.percentage
                        user_instance = User.objects.filter(supplier__id=j.supplier_id).first()
                        rfx_item_supplier = RFXItemSupplier.objects.filter(rfx_supplier__user=user_instance, rfx_item=rfx_item).order_by("-order").first()
                        RFXAward.objects.create(
                            user=user_instance,
                            rfx=rfx,
                            rfx_item=rfx_item,
                            percentage=j.percentage,
                            price=rfx_item_supplier.total_amount,
                        )
                        rfx_item_supplier.percentage = j.percentage
                        rfx_item_supplier.save()
                        set_supplier_ids.add(j.supplier_id)
                    if total_percentage != 100:
                        transaction.set_rollback(True)
                        error = Error(code="RFX_10", message=RFXError.RFX_10)
                        return RFXAwardCreate(error=error, status=False)
            elif rfx.split_order == 1:
                for i in items:
                    rfx_item = RFXItem.objects.filter(id=i.rfx_item_id).first()
                    user_instance = User.objects.filter(supplier__id=i.suppliers[0].supplier_id).first()
                    rfx_item_supplier = RFXItemSupplier.objects.filter(rfx_supplier__user=user_instance, rfx_item=rfx_item).order_by("-order").first()
                    RFXAward.objects.create(
                        user=user_instance,
                        rfx=rfx,
                        rfx_item=rfx_item,
                        percentage=100,
                        price=rfx_item_supplier.total_amount
                    )
                    rfx_item_supplier.percentage = 100
                    rfx_item_supplier.save()

                    set_supplier_ids.add(i.suppliers[0].supplier_id)
            supplier_ids = list(set_supplier_ids)
            suppliers = Supplier.objects.filter(id__in=supplier_ids)
            for j in suppliers:
                send_mail_PO_NPDOC14("RFX_PO_NPDOC14", rfx, j)

            rfx.status = 4
            rfx.save()
            RFXSupplier.objects.filter(rfx=rfx, user__supplier__id__in=supplier_ids).update(quote_submited_status=4)
            rfx_supplier_instances = RFXSupplier.objects.filter(rfx=rfx).exclude(quote_submited_status=4)
            for j in rfx_supplier_instances:
                j.quote_submited_status = 5
                j.save()
            return RFXAwardCreate(status=True)
        except Exception as error:
            print(error)
            transaction.set_rollback(True)
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXAwardCreate(error=error, status=False)


class RFXSupplierAttachmentInput(graphene.InputObjectType):
    attachment = Upload(required=True)
    id = graphene.String()


class RFXSupplierInput(graphene.InputObjectType):
    commercial_terms = graphene.Boolean()
    note_for_buyer = graphene.String()
    attachments = graphene.List(RFXSupplierAttachmentInput)


class RFXItemSupplierInput(graphene.InputObjectType):
    rfx_item_id = graphene.String(required=True)
    informations = graphene.String()
    proposals = graphene.String()
    total_amount = graphene.Float()
    unit_price = graphene.Float()
    vat_tax = graphene.Float()


class RFXItemSupplierCreate(graphene.Mutation):
    status = graphene.Boolean(default_value=False)
    error = graphene.Field(Error)

    class Arguments:
        items = graphene.List(RFXItemSupplierInput)
        rfx_id = graphene.String(required=True)
        options = RFXSupplierInput()

    def mutate(root, info, rfx_id, items, options=None):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isSupplier():
                rfx = RFXData.objects.filter(id=rfx_id).first()
                if rfx.status == 3:
                    error = Error(code="RFX_07", message=RFXError.RFX_07)
                    return RFXItemSupplierCreate(error=error, status=False)
                if rfx.due_date <= timezone.now().astimezone(tz=pytz.UTC):
                    return RFXItemSupplierCreate(error=Error(code="RFX_07", message=RFXError.RFX_07), status=False)
                rfx.email_date = timezone.now()
                rfx.is_send = True
                rfx.save()
                rfx_supplier = RFXSupplier.objects.filter(rfx=rfx, user=user).first()
                if rfx_supplier.is_joined == False:
                    transaction.set_rollback(True)
                    error = Error(code="RFX_06", message=RFXError.RFX_06)
                    return RFXItemSupplierCreate(error=error, status=False)

                if rfx.rfx_type == 1 \
                        and any(
                    item.get("informations") is None
                    or item.get("informations") == "" for item in items
                ):
                    return RFXItemSupplierCreate(error=Error(code="RFX_11", message=RFXError.RFX_11), status=False)
                if rfx.rfx_type == 2 \
                        and (
                        item.get("proposals") is None
                        or item.get("proposals") == "" for item in items
                ):
                    return RFXItemSupplierCreate(error=Error(code="RFX_12", message=RFXError.RFX_12), status=False)

                order = 0
                order_instance = RFXItemSupplier.objects.filter(rfx=rfx, rfx_supplier=rfx_supplier).order_by("-order").first()
                if order_instance is not None:
                    order = order_instance.order + 1

                if rfx.rfx_type == 3:
                    if any(item.get("unit_price") is None for item in items):
                        return RFXItemSupplierCreate(error=Error(code="RFX_13", message=RFXError.RFX_13), status=False)
                    if any(item.get("vat_tax") is None for item in items):
                        return RFXItemSupplierCreate(error=Error(code="RFX_14", message=RFXError.RFX_14), status=False)

                if options is not None:
                    # rfx_supplier.commercial_terms=options.commercial_terms
                    rfx_supplier.note_for_buyer = options.note_for_buyer

                sub_total = 0
                for item in items:
                    if item.get("vat_tax") and (item.vat_tax < 0 or item.vat_tax > 100):
                        transaction.set_rollback(True)
                        error = Error(code="RFX_08", message=RFXError.RFX_08)
                        return RFXItemSupplierCreate(error=error, status=False)
                    rfx_item = RFXItem.objects.filter(id=item.rfx_item_id).first()
                    total_amount = item.total_amount if item.get("total_amount") is not None else 0
                    rfx_item_supplier = RFXItemSupplier(
                        rfx=rfx,
                        rfx_supplier=rfx_supplier,
                        rfx_item=rfx_item,
                        informations=item.informations,
                        proposals=item.proposals,
                        total_amount=total_amount,
                        order=order,
                        unit_price=item.unit_price,
                        vat_tax=item.vat_tax,
                        submitted_date=timezone.now()
                    )
                    rfx_item_supplier.save()
                    sub_total += total_amount

                rfx_supplier.sub_total = sub_total
                rfx_supplier.quote_submited_status = 2
                rfx_supplier.save()

                if options is not None:
                    if options.attachments is not None and len(options.attachments) > 0:
                        unchanged_attachment_list = []
                        for i in options.attachments:
                            if i.id is not None and i.id != "":
                                unchanged_attachment_list.append(i.id)
                        RFXAttachment.objects.filter(rfx=rfx, user=user, upload_by=2).exclude(id__in=unchanged_attachment_list).delete()
                        for i in options.attachments:
                            if i.id is None or i.id == "":
                                rfx_attachment = RFXAttachment(
                                    rfx=rfx,
                                    attachment=i.attachment,
                                    upload_by=2,
                                    user=user
                                )
                                rfx_attachment.save()

                min_price = RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2).aggregate(Min('sub_total')).get('sub_total__min')
                rfx_supplier_instances = RFXSupplier.objects.filter(rfx=rfx, quote_submited_status=2)
                for k in rfx_supplier_instances:
                    if k.sub_total == min_price:
                        k.is_best_price = True
                    else:
                        k.is_best_price = False
                    k.save(update_fields=['is_best_price'])

                return RFXItemSupplierCreate(status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXItemSupplierCreate(error=error, status=False)
        except Exception as err:
            transaction.set_rollback(True)
            print(err)
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXItemSupplierCreate(error=error, status=False)


class RFXDelete(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.String(required=True)

    def mutate(root, info, id):
        RFXAttachment.objects.filter(rfx_id=id).delete()
        RFXAward.objects.filter(rfx_id=id).delete()
        RFXItemSupplier.objects.filter(rfx_id=id).delete()
        RFXSupplier.objects.filter(rfx_id=id).delete()
        RFXItem.objects.filter(rfx_id=id).delete()
        RFXData.objects.get(pk=id).delete()
        return RFXDelete(status=True)


class RFXClearAll(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        pass

    def mutate(root, info):
        RFXAttachment.objects.all().delete()
        RFXAward.objects.all().delete()
        RFXItemSupplier.objects.all().delete()
        RFXSupplier.objects.all().delete()
        RFXItem.objects.all().delete()
        RFXData.objects.all().delete()
        return RFXClearAll(status=True)


class RFXSupplierTermsUpdateInput(graphene.InputObjectType):
    rfx_id = graphene.String(required=True)
    commercial_terms = graphene.Boolean(required=True)


class RFXSupplierTermsUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        input = RFXSupplierTermsUpdateInput(required=True)

    def mutate(root, info, input):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isSupplier():
                rfx_supplier_instance = RFXSupplier.objects.filter(user=user, rfx_id=input.rfx_id).first()
                rfx_supplier_instance.commercial_terms = input.commercial_terms
                rfx_supplier_instance.save()
                return RFXSupplierTermsUpdate(status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXSupplierTermsUpdate(error=error, status=False)
        except:
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXSupplierTermsUpdate(error=error, status=False)


class RFXTimeViewMinutesUpdate(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        view_in_minutes = graphene.Int(required=True)

    def mutate(root, info, view_in_minutes):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if user.isAdmin():
                RFXData.objects.all().update(time_view_minutes=view_in_minutes)
                return RFXTimeViewMinutesUpdate(status=True)
            else:
                error = Error(code="RFX_01", message=RFXError.RFX_01)
                return RFXTimeViewMinutesUpdate(error=error, status=False)
        except:
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXTimeViewMinutesUpdate(error=error, status=False)


class RFXSupplierConfirm(graphene.Mutation):
    status = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        rfx_id = graphene.String(required=True)

    @transaction.atomic
    def mutate(root, info, rfx_id):
        try:
            token = GetToken.getToken(info)
            user = token.user
            if not user.isSupplier():
                return RFXSupplierConfirm(
                    error=Error(code="RFX_01", message=RFXError.RFX_01),
                    status=False
                )
            rfx = RFXData.objects.filter(id=rfx_id).first()
            if rfx is None:
                return RFXSupplierConfirm(
                    error=Error(code="RFX_15", message=RFXError.RFX_15),
                    status=False
                )
            rfx_supplier = RFXSupplier.objects.filter(
                rfx=rfx,
                user=user,
                quote_submited_status=4,
            ).first()
            if rfx_supplier is None:
                return RFXSupplierConfirm(
                    error=Error(code="RFX_16", message=RFXError.RFX_16),
                    status=False
                )
            if rfx_supplier.is_confirm:
                return RFXSupplierConfirm(
                    error=Error(code="RFX_17", message=RFXError.RFX_17),
                    status=False
                )
            rfx_supplier.is_confirm = True
            rfx_supplier.save()
            if all(
                    x.is_confirm for x in RFXSupplier.objects.filter(
                        rfx=rfx,
                        quote_submited_status=4
                    )
            ):
                rfx.status = 9
                rfx.save()

            return RFXSupplierConfirm(status=True)
        except Exception as error:
            transaction.set_rollback(True)
            error = Error(code="RFX_02", message=RFXError.RFX_02)
            return RFXSupplierConfirm(error=error, status=False)


class Mutation(graphene.ObjectType):
    rfx_create = RFXCreate.Field()
    rfx_update = RFXUpdate.Field()
    rfx_status_update = RFXStatusUpdate.Field()
    rfx_delete = RFXDelete.Field()
    rfx_clear_all = RFXClearAll.Field()

    rfx_time_view_update = RFXTimeViewMinutesUpdate.Field()

    rfx_supplier_quote_submited_status_update = RFXSupplierQuoteSubmitedStatusUpdate.Field()
    rfx_supplier_is_joined_update = RFXIsJoinedUpdate.Field()
    rfx_supplier_terms_update = RFXSupplierTermsUpdate.Field()

    rfx_awarded_create = RFXAwardCreate.Field()

    rfx_item_supplier_create = RFXItemSupplierCreate.Field()

    rfx_supplier_confirm = RFXSupplierConfirm.Field()
