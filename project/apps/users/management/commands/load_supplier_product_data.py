import os

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction


from apps.users.models import (
    SupplierProduct,
    SupplierFlashSale,
    ProductType,
    ProductConfirmStatus,
    SupplierProductImage,
    SupplierProductFlashSale
)

class Command(BaseCommand):
    def update(self):
        try:
            if SupplierProduct.objects.all().count() == 0:
                for flash_sale in SupplierFlashSale.objects.all().order_by("id"):
                    if flash_sale.is_confirmed == 1:
                        confirmed_status = ProductConfirmStatus.APPROVED
                    elif flash_sale.is_confirmed == 2:
                        confirmed_status = ProductConfirmStatus.WAITING
                    elif flash_sale.is_confirmed == 3:
                        confirmed_status = ProductConfirmStatus.REJECTED
                    else:
                        confirmed_status = None
                    supplier_product = SupplierProduct.objects.create(
                        sku_number = flash_sale.sku_number,
                        description = flash_sale.description,
                        type = ProductType.FLASH_SALE,
                        product_name = "",
                        is_visibility = flash_sale.is_active,
                        confirmed_status = confirmed_status,
                        user_supplier = flash_sale.user_supplier,
                        reach_number = flash_sale.reach_number,
                        click_number = flash_sale.click_number
                    )
                    if flash_sale.picture is not None:
                        try: 
                            image = File(flash_sale.picture, os.path.basename(flash_sale.picture.path))
                            SupplierProductImage.objects.create(
                                supplier_product = supplier_product,
                                image = image
                            )
                            flash_sale.picture.close()
                        except Exception as e:
                            pass
                    SupplierProductFlashSale.objects.create(
                        supplier_product = supplier_product,
                        initial_price = flash_sale.initial_price,
                        discounted_price = round(flash_sale.initial_price*(1-flash_sale.percentage/100))
                    )
                print("Transfer success")
                return
            print("Already update")
            return
        except Exception as error:
            print("----------------------> Error", error)
        
    def handle(self, *args, **options):
        print("----------------------> Loading")
        self.update()