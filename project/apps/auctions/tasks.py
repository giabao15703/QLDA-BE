import os


from apps.auctions.models import Auction, AuctionBid, AuctionSupplier
from apps.auctions.views import AuctionReports
from apps.master_data.models import EmailTemplates, EmailTemplatesTranslation
from apps.payment.models import PaymentAuction

from celery import Celery

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.template import Template, Context

app = Celery('apps', broker=settings.RABBITMQ_URL)

@app.task(name='apps.auctions.tasks.check_status')
def check_status():
    server_time = timezone.now()
    auction_list = Auction.objects.filter().exclude(status__in=[1, 4])
    for auction in auction_list:
        end_time = auction.extend_time or auction.end_time
        if server_time < auction.start_time:
            auction.status = 2
            auction.save()
            reminder_deposit(auction)
        if auction.start_time <= server_time <= end_time:
            auction.status = 3
            auction.save()
            auction_suppliers = AuctionSupplier.objects.filter(auction=auction)
            for auction_supplier in auction_suppliers:
                if auction_supplier.supplier_status == 5:
                    auction_supplier.supplier_status = 6
                if auction_supplier.supplier_status == 1:
                    auction_supplier.supplier_status = 7
                auction_supplier.save()
        if auction.status == 3 and server_time > end_time:
            auction.status = 4
            auction.save()
            auction_supplier = AuctionSupplier.objects.filter(auction_id=auction.id, is_accept=True)
            for supplier in auction_supplier:
                number_bid = AuctionBid.objects.filter(user_id=supplier.user_id, auction_id=auction.id).count()
                email_supplier = EmailTemplatesTranslation.objects.filter(
                    email_templates__item_code="AuctionEndSupplier", language_code=supplier.user.language.item_code
                )
                if not email_supplier:
                    email_supplier = EmailTemplates.objects.filter(item_code="AuctionEndSupplier")
                email_supplier = email_supplier.first()
                title = email_supplier.title
                t = Template(email_supplier.content)
                c = Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "name": supplier.user.full_name,
                        "auction_title": auction.title,
                        "auction_item_code": auction.item_code,
                        "number_bid": number_bid,
                    }
                )
                output = t.render(c)
                try:
                    send_mail(title, output, "NextPro <no-reply@nextpro.io>", [supplier.user.email], html_message=output, fail_silently=True)
                except:
                    print("fail mail")

            # buyer
            total_number_bid = AuctionBid.objects.filter(auction_id=auction.id).count()
            email_buyer = EmailTemplatesTranslation.objects.filter(
                email_templates__item_code="AuctionEndBuyer", language_code=auction.user.language.item_code
            )
            if not email_buyer:
                email_buyer = EmailTemplates.objects.filter(item_code="AuctionEndBuyer")
            email_buyer = email_buyer.first()

            title = email_buyer.title
            messages = Template(email_buyer.content).render(
                Context(
                    {
                        "image": "https://api.nextpro.io/static/logo_mail.png",
                        "name": auction.user.full_name,
                        "auction_title": auction.title,
                        "auction_item_code": auction.item_code,
                        "total_number_bid": total_number_bid,
                    }
                )
            )
            try:
                language_code = auction.user.language.item_code
                AuctionReports.report(auction=auction, language_code=language_code)
                file_path = os.path.join(settings.MEDIA_ROOT, 'auction_reports', f'''{auction.item_code}.xlsx''')
                email = EmailMessage(subject=title, body=messages, from_email="NextPro <no-reply@nextpro.io>", to=[auction.user.email])
                email.attach_file(file_path)
                email.content_subtype = "html"
                email.send()
            except Exception as err:
                print({"fail mail": err})

def reminder_deposit(auction):
    delta_time = (timezone.now() - auction.created).days
    if delta_time == 1:
        auction_supplier = AuctionSupplier.objects.filter(auction=auction, supplier_status=1)
        for supplier in auction_supplier:
            if (
                not PaymentAuction.objects.filter(auction=auction, history__user_payment__user=supplier.user).exists()
                and supplier.email_reminder_deposit is None
            ):
                supplier.email_reminder_deposit = timezone.now()
                supplier.save()
                email_template = EmailTemplatesTranslation.objects.filter(
                    email_templates__item_code="ReminderDepositAuction", language_code=supplier.user.language.item_code
                )
                if not email_template:
                    email_template = EmailTemplates.objects.filter(item_code="ReminderDepositAuction")
                email_template = email_template.first()
                title = Template(email_template.title).render(Context({'auction_item_code': auction.item_code}))
                message = Template(email_template.content).render(
                    Context(
                        {
                            "image": "https://api.nextpro.io/static/logo_mail.png",
                            "name": auction.user.full_name,
                            "auction_item_code": auction.item_code,
                            "buyer_name": auction.user.buyer.company_full_name,
                        }
                    )
                )
                try:
                    send_mail(title, message, "NextPro <no-reply@nextpro.io>", [supplier.user.email], html_message=message, fail_silently=True)
                except:
                    print("fail mail")
