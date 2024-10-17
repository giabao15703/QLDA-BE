from django.core.management.base import BaseCommand, CommandError
from apps.master_data.models import (
    AuctionType,
    UnitofMeasure,
    Category,
    ClusterCode,
    SubClusterCode,
    Currency,
    DeliveryTerm,
    EmailTemplates,
    FamilyCode,
    Gender,
    IndustryCluster,
    PaymentTerm,
    Reason,
    NumberofEmployee,
    Position,
    Language,
    Industry,
    IndustrySubSectors,
    IndustrySectors,
    Country,
    TechnicalWeighting,
    ClientFocus,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        unit_of_measures = UnitofMeasure.objects.all()
        for unit_of_measure in unit_of_measures:
            unit_of_measure.translations.update_or_create(language_code="en", defaults={"name": unit_of_measure.name})
            unit_of_measure.save()
        auction_types = AuctionType.objects.all()
        for auction_type in auction_types:
            auction_type.translations.update_or_create(language_code="en", defaults={"name": auction_type.name})
            auction_type.save()
        categories = Category.objects.all()
        for category in categories:
            category.translations.update_or_create(language_code="en", defaults={"name": category.name})
            category.save()
        cluster_codes = ClusterCode.objects.all()
        for cluster_code in cluster_codes:
            cluster_code.translations.update_or_create(language_code="en", defaults={"name": cluster_code.name})
            cluster_code.save()
        currencies = Currency.objects.all()
        for currency in currencies:
            currency.translations.update_or_create(language_code="en", defaults={"name": currency.name})
            currency.save()
        delivery_terms = DeliveryTerm.objects.all()
        for delivery_term in delivery_terms:
            delivery_term.translations.update_or_create(language_code="en", defaults={"name": delivery_term.name})
            delivery_term.save()
        email_templates = EmailTemplates.objects.all()
        for email_template in email_templates:
            email_template.translations.update_or_create(
                language_code="en", defaults={"title": email_template.title, "content": email_template.content}
            )
            email_template.save()
        family_codes = FamilyCode.objects.all()
        for family_code in family_codes:
            family_code.translations.update_or_create(language_code="en", defaults={"name": family_code.name})
            family_code.save()
        genders = Gender.objects.all()
        for gender in genders:
            gender.translations.update_or_create(language_code="en", defaults={"name": gender.name})
            gender.save()
        industry_clusters = IndustryCluster.objects.all()
        for industry_clusters in industry_clusters:
            industry_clusters.translations.update_or_create(language_code="en", defaults={"name": industry_clusters.name})
            industry_clusters.save()
        payment_terms = PaymentTerm.objects.all()
        for payment_term in payment_terms:
            payment_term.translations.update_or_create(language_code="en", defaults={"name": payment_term.name})
            payment_term.save()
        reasons = Reason.objects.all()
        for reason in reasons:
            reason.translations.update_or_create(language_code="en", defaults={"name": reason.name})
            reason.save()
        number_of_employees = NumberofEmployee.objects.all()
        for number_of_employee in number_of_employees:
            number_of_employee.translations.update_or_create(language_code="en", defaults={"name": number_of_employee.name})
            number_of_employee.save()
        positions = Position.objects.all()
        for position in positions:
            position.translations.update_or_create(language_code="en", defaults={"name": position.name})
            position.save()
        languages = Language.objects.all()
        for language in languages:
            language.translations.update_or_create(language_code="en", defaults={"name": language.name})
            language.save()
        industries = Industry.objects.all()
        for industry in industries:
            industry.translations.update_or_create(language_code="en", defaults={"name": industry.name})
            industry.save()
        industry_sub_sectors = IndustrySubSectors.objects.all()
        for industry_sub_sector in industry_sub_sectors:
            industry_sub_sector.translations.update_or_create(language_code="en", defaults={"name": industry_sub_sector.name})
            industry_sub_sector.save()
        industry_sectors = IndustrySectors.objects.all()
        for industry_sector in industry_sectors:
            industry_sector.translations.update_or_create(language_code="en", defaults={"name": industry_sector.name})
            industry_sector.save()
        countries = Country.objects.all()
        for country in countries:
            country.translations.update_or_create(language_code="en", defaults={"name": country.name})
            country.save()

        sub_cluster_codes = SubClusterCode.objects.all()
        for sub_cluster_code in sub_cluster_codes:
            sub_cluster_code.translations.update_or_create(language_code="en", defaults={"name": sub_cluster_code.name})
            sub_cluster_code.save()
        technical_weightings = TechnicalWeighting.objects.all()
        for technical_weighting in technical_weightings:
            technical_weighting.translations.update_or_create(language_code="en", defaults={"name": technical_weighting.name})
            technical_weighting.save()
        client_focuses = ClientFocus.objects.all()
        for client_focus in client_focuses:
            client_focus.translations.update_or_create(language_code="en", defaults={"name": client_focus.name})
            client_focus.save()

        print("Done")