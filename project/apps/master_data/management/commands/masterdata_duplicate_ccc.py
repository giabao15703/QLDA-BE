from django.core.management.base import BaseCommand, CommandError
from apps.master_data.models import FamilyCode, ClusterCode, SubClusterCode, Category

class Command(BaseCommand):
    def handle(self, *args, **options):
        family_codes = FamilyCode.objects.all()
        total = 0
        for family_code in family_codes:
            if family_code.clusterCode.count() == 0:
                cluster_code = ClusterCode(
                    family_code = family_code,
                    item_code = str(ClusterCode.objects.count()) + '1',
                    name = family_code.name,
                    status = True,
                )
                cluster_code.save()
            else:
                for cluster_code in family_code.clusterCode.all():
                    if cluster_code.subClusterCode.count() == 0:
                        sub_cluster_code = SubClusterCode(
                            cluster_code = cluster_code,
                            item_code = str(SubClusterCode.objects.count()) + "1",
                            name = cluster_code.name,
                            status = True,
                        )
                        sub_cluster_code.save()
                    else:
                        for sub_cluster_code in cluster_code.subClusterCode.all():
                            if sub_cluster_code.category.count() == 0:
                                category = Category(
                                    sub_cluster_code = sub_cluster_code,
                                    item_code = str(Category.objects.count()) + "1",
                                    name = sub_cluster_code.name,
                                    status = True,
                                )
                                category.save()
