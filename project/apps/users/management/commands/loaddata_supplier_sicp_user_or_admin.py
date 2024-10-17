from django.core.management.base import BaseCommand
from apps.users.models import SupplierSICPFile
class Command(BaseCommand):
    def handle(self, *args, **options):
        sicp_files = SupplierSICPFile.objects.all()
        for i in sicp_files:
            if i.sicp_type == 1 or i.sicp_type == 2 or i.sicp_type == 3 or i.sicp_type == 4 or i.sicp_type == 5:
                i.user_or_admin = 1
            elif i.sicp_type == 6:
                i.user_or_admin = 2
            else:
                i.user_or_admin = 3
            i.save()
        print("Done")