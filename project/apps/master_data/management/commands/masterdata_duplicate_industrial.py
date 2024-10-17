from django.core.management.base import BaseCommand, CommandError
from apps.master_data.models import Industry, IndustryCluster, IndustrySectors, IndustrySubSectors

class Command(BaseCommand):
    def handle(self, *args, **options):
        industries = Industry.objects.all()
        for industry in industries:
            if industry.industryCluster.count() == 0:
                industry_cluster = IndustryCluster(
                    industry = industry,
                    item_code = industry.item_code + '1',
                    name = industry.name,
                    status = True,
                )
                industry_cluster.save()
            else:
                for industry_cluster in industry.industryCluster.all():
                    if industry_cluster.industrySectors.count() == 0:
                        industry_sectors = IndustrySectors(
                            industry_cluster = industry_cluster,
                            item_code = industry_cluster.item_code + "1",
                            name = industry_cluster.name,
                            status = True,
                        )
                        industry_sectors.save()
                    else:
                        for industry_sectors in industry_cluster.industrySectors.all():
                            if industry_sectors.industrySubSectors.count() == 0:
                                industrySubSectors = IndustrySubSectors(
                                    industry_sectors = industry_sectors,
                                    item_code = industry_sectors.item_code + "1",
                                    name = industry_sectors.name,
                                    status = True,
                                )
                                industrySubSectors.save()
        print("Done")
