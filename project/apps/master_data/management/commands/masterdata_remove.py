from django.core.management.base import BaseCommand, CommandError
from apps.master_data.models import FamilyCode, ClusterCode, SubClusterCode, Category

class Command(BaseCommand):

    def handle(self, *args, **options):

        family_codes = FamilyCode.objects.all()

        for family_code in family_codes:

            if family_code.id == 20:

                for cluster_code in family_code.clusterCode.all():

                    for sub_cluster_code in cluster_code.subClusterCode.all():

                        for category in sub_cluster_code.category.all():

                            category.delete()

                        sub_cluster_code.delete()

                    cluster_code.delete()

                family_code.delete()

        print("Done")
