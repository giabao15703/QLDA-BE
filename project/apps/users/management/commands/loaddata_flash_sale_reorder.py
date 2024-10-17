from django.core.management.base import BaseCommand
from apps.users.models import SupplierFlashSale
class Command(BaseCommand):
    def handle(self, *args, **options):
        flash_sales = SupplierFlashSale.objects.all()
        count = 0
        for i in flash_sales:
            i.re_order = count
            i.save()
            count += 1
        print("Done")