import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from .translation import TranslationProxy
from django.core.validators import MinValueValidator,MaxValueValidator

class PromotionApplyScope(models.TextChoices):
    FOR_BUYER = "for_buyer", _("For_buyer")
    FOR_SUPPLIER_ALL_SCOPE = "for_supplier_all_scope", _("For_supplier_all_scope")
    FOR_SUPPLIER_PROFILE_FEATURES = "for_supplier_profile_features", _("For_supplier_profile_features")
    FOR_SUPPLIER_SICP = "for_supplier_sicp", _("For_supplier_sicp")
    FOR_SUPPLIER = "for_supplier", _("For_supplier")

class Country(models.Model):
    item_code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_country'

class CountryTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    country = models.ForeignKey(Country, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "country"),)
        db_table = 'master_data_country_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, country_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.country_id,
        )

class CountryState(models.Model):
    name = models.CharField(max_length=256)
    state_code = models.CharField(max_length=10)
    country = models.ForeignKey(Country, related_name="state", on_delete=models.CASCADE)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, country_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.country_id,
        )

    class Meta:
        unique_together = (("state_code", "country"),)
        db_table = 'master_data_country_state'

class CountryStateTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    country_state = models.ForeignKey(CountryState, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "country_state"),)
        db_table = 'master_data_country_state_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, country_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.country_id,
        )


class FamilyCode(models.Model):
    item_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_family_code'

class FamilyCodeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    family_code = models.ForeignKey(FamilyCode, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "family_code"),)
        db_table = 'master_data_family_code_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, family_code_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.family_code_id,
        )

class ClusterCode(models.Model):
    family_code = models.ForeignKey(FamilyCode, on_delete=models.CASCADE, related_name='clusterCode')
    item_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_cluster_code'

class ClusterCodeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    cluster_code = models.ForeignKey(ClusterCode, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "cluster_code"),)
        db_table = 'master_data_cluster_code_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, cluster_code_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.cluster_code_id,
        )

class SubClusterCode(models.Model):
    cluster_code = models.ForeignKey(ClusterCode, on_delete=models.CASCADE, related_name='subClusterCode')
    item_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_sub_cluster_code'

class SubClusterCodeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    sub_cluster_code = models.ForeignKey(SubClusterCode, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "sub_cluster_code"),)
        db_table = 'master_data_sub_cluster_code_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, sub_cluster_code_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.sub_cluster_code_id,
        )

class Category(models.Model):
    sub_cluster_code = models.ForeignKey(SubClusterCode, on_delete=models.CASCADE, related_name='category')
    item_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_category'

class CategoryTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    category = models.ForeignKey(Category, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "category"),)
        db_table = 'master_data_category_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, category_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.category_id,
        )

class Currency(models.Model):
    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=16, unique=True)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_currency'

class CurrencyTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    currency = models.ForeignKey(Currency, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "currency"),)
        db_table = 'master_data_currency_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, currency_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.currency_id,
        )

class ContractType(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_contract_type'

class ContractTypeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    contract_type = models.ForeignKey(ContractType, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "contract_type"),)
        db_table = 'master_data_contract_type_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, contract_type_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.contract_type_id,
        )

class PaymentTerm(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    class Meta:
        db_table = 'master_data_payment_term'

class PaymentTermTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    payment_term = models.ForeignKey(PaymentTerm, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "payment_term"),)
        db_table = 'master_data_payment_term_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, payment_term_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.payment_term_id,
        )

class DeliveryTerm(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_delivery_term'

class DeliveryTermTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    delivery_term = models.ForeignKey(DeliveryTerm, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "delivery_term"),)
        db_table = 'master_data_delivery_term_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, delivery_term_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.delivery_term_id,
        )

class UnitofMeasure(models.Model):
    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=16, unique=True)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    class Meta:
        db_table = 'master_data_unit_of_measure'

class UnitofMeasureTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    unit_of_measure = models.ForeignKey(UnitofMeasure, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "unit_of_measure"),)
        db_table = 'master_data_unit_of_measure_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,unit_of_measure_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.unit_of_measure_id,
        )

class EmailTemplates(models.Model):
    item_code = models.CharField(max_length=25, unique=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=2000)
    variables = models.TextField(max_length=2000, null=True)
    status = models.BooleanField(null=True, default=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(null=True, blank=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'master_data_email_templates'

class EmailTemplatesTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    email_templates = models.ForeignKey(EmailTemplates, related_name="translations", on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    content = models.TextField(max_length=2000)

    class Meta:
        unique_together = (("language_code", "email_templates"),)
        db_table = 'master_data_email_templates_translation'

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, title=%r,email_templates_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.title,
            self.email_templates_id,
        )

class NumberofEmployee(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_number_of_employee'

class NumberofEmployeeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    number_of_employee = models.ForeignKey(NumberofEmployee, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "number_of_employee"),)
        db_table = 'master_data_number_of_employee_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,number_of_employee_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.number_of_employee_id,
        )

class Gender(models.Model):
    name = models.CharField(max_length=16)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    class Meta:
        db_table = 'master_data_gender'

class GenderTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    gender = models.ForeignKey(Gender, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "gender"),)
        db_table = 'master_data_gender_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,gender_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.gender_id,
        )

class TechnicalWeighting(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_technical_weighting'

class TechnicalWeightingTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    technical_weighting = models.ForeignKey(TechnicalWeighting, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "technical_weighting"),)
        db_table = 'master_data_technical_weighting_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,technical_weighting_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.technical_weighting_id,
        )

class AuctionType(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_auction_type'

class AuctionTypeTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    auction_type = models.ForeignKey(AuctionType, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "auction_type"),)
        db_table = 'master_data_auction_type_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,auction_type_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.auction_type_id,
        )

class Position(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_position'

class PositionTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    position = models.ForeignKey(Position, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "position"),)
        db_table = 'master_data_position_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,position_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.position_id,
        )

class Level(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_level'

class LevelTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    level = models.ForeignKey(Level, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "level"),)
        db_table = 'master_data_level_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,level_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.level_id,
        )

class ClientFocus(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_client_focus'

class ClientFocusTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    client_focus = models.ForeignKey(ClientFocus, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "client_focus"),)
        db_table = 'master_data_client_focus_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,client_focus_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.client_focus_id,
        )

class Industry(models.Model):
    item_code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_industry'

def sponsor_logo_directory_path(instance, filename):
    return os.path.join(str('sponsor'), "{}.{}".format('sponsor', filename.split('.')[-1]))

class IndustryTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    industry = models.ForeignKey(Industry, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "industry"),)
        db_table = 'master_data_industry_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,industry_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.industry_id,
        )

class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=sponsor_logo_directory_path, null=True)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_sponsor'

class SponsorTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    sponsor = models.ForeignKey(Sponsor, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "sponsor"),)
        db_table = 'master_data_sponsor_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,sponsor_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.sponsor_id,
        )

class Reason(models.Model):
    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=16, unique=True)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_reason'

class ReasonTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    reason = models.ForeignKey(Reason, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "reason"),)
        db_table = 'master_data_reason_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,reason_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.reason_id,
        )

class Language(models.Model):
    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=16, unique=True)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_language'


class LanguageTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    language = models.ForeignKey(Language, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "language"),)
        db_table = 'master_data_language_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,language_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.language_id,
        )

class IndustryCluster(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='industryCluster')
    item_code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_industry_cluster'

class IndustryClusterTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    industry_cluster = models.ForeignKey(IndustryCluster, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "industry_cluster"),)
        db_table = 'master_data_industry_cluster_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,industry_cluster_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.industry_cluster_id,
        )

class IndustrySectors(models.Model):
    industry_cluster = models.ForeignKey(IndustryCluster, on_delete=models.CASCADE, related_name='industrySectors')
    item_code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_industry_sectors'

class IndustrySectorsTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    industry_sectors = models.ForeignKey(IndustrySectors, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "industry_sectors"),)
        db_table = 'master_data_industry_sectors_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,industry_sectors_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.industry_sectors_id,
        )

class IndustrySubSectors(models.Model):
    industry_sectors = models.ForeignKey(IndustrySectors, on_delete=models.CASCADE, related_name='industrySubSectors')
    item_code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_industry_sub_sectors'

class IndustrySubSectorsTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    industry_sub_sectors = models.ForeignKey(IndustrySubSectors, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "industry_sub_sectors"),)
        db_table = 'master_data_industry_sub_sectors_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,industry_sub_sectors_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.industry_sub_sectors_id,
        )
class Promotion(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2048)
    discount = models.FloatField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    status = models.BooleanField(null=True, default=True)
    translated = TranslationProxy()
    apply_for_buyer = models.BooleanField(default=False)
    apply_for_supplier = models.BooleanField(default=False)
    apply_for_advertisement = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)
    user_given = models.CharField(max_length=100, null=True, blank=True)
    user_given_email = models.CharField(max_length=50, null=True, blank=True)
    commission = models.FloatField(null=True, blank=True)
    apply_scope = models.CharField(max_length=32, choices=PromotionApplyScope.choices, null=True, blank=True)

    class Meta:
        db_table = 'master_data_promotion'

class PromotionUserUsed(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="promotion_users")
    user_used = models.CharField(max_length=100, null=True, blank=True)
    user_used_email = models.CharField(max_length=50, null=True, blank=True)
    user_name = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=225, null=True, blank=True)
    date_used = models.DateTimeField(null=True, blank=True)
    real_amount = models.FloatField(null=True, blank=True)
    amount_after_discount = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'master_data_promotion_user_used'

class PromotionTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    promotion = models.ForeignKey(Promotion, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=2048)

    class Meta:
        unique_together = (("language_code", "promotion"),)
        db_table = 'master_data_promotion_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,promotion_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.promotion_id,
        )

class SupplierList(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    translated = TranslationProxy()

    class Meta:
        db_table = 'master_data_supplier_list'

class SupplierListTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    supplier_list = models.ForeignKey(SupplierList, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "supplier_list"),)
        db_table = 'master_data_supplier_list_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r,supplier_list_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.supplier_list_id,
        )

class EmailList(models.Model):
    email = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'master_data_email_list'

class ExchangeRate(models.Model):
    unit_of_measures_name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=128, unique=True)
    exchange_rate = models.FloatField()
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'master_data_exchange_rate'

class Coupon(models.Model):
    coupon_program = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    commission = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    status = models.BooleanField(null=True, default=True)

    class Meta:
        db_table = 'master_data_coupon'

class Bank(models.Model):
    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=128, unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'master_data_bank'



class Voucher(models.Model):
    voucher_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    label = models.CharField(max_length=255,blank=True,default='')
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_voucher'

class VoucherTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    voucher = models.ForeignKey(Voucher, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "voucher"),)
        db_table = 'master_data_voucher_translation'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, category_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.name,
            self.voucher_id,
        )
    
class BuyerClubVoucher(models.Model):
    voucher_code = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    standard = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    gold = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    platinum = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    diamond = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    label = models.CharField(max_length=255,blank=True,default='')
    translated = TranslationProxy()

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'master_data_buyer_club_voucher'

class BuyerClubVoucherTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    buyer_club_voucher = models.ForeignKey(BuyerClubVoucher, related_name="translations", on_delete=models.CASCADE)
    description = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "buyer_club_voucher"),)
        db_table = 'master_data_buyer_club_voucher_translation'

    def __str__(self) -> str:
        return self.description

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, category_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.description,
            self.buyer_club_voucher_id,
        )
class WarrantyTerm(models.Model):
    warranty_code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'master_data_warranty_term'

class WarrantyTermTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    warranty_term = models.ForeignKey(WarrantyTerm, related_name="translations", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "warranty_term"),)
        db_table = 'master_data_warranty_term_translation'

    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, warranty_term_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.description,
            self.warranty_term_id,
        )

class SetProductAdvertisement(models.Model):
    description = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    duration = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(365)])
    serviceFee = models.FloatField(null=True)
    translated = TranslationProxy()

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'master_data_set_product_advertisement'

class SetProductAdvertisementTranslation(models.Model):
    language_code = models.CharField(max_length=10)
    set_product_advertisement = models.ForeignKey(SetProductAdvertisement, related_name="translations", on_delete=models.CASCADE)
    description = models.CharField(max_length=256)

    class Meta:
        unique_together = (("language_code", "set_product_advertisement"),)
        db_table = 'master_data_set_product_advertisement_translation'

    def __str__(self) -> str:
        return self.description

    def __repr__(self) -> str:
        class_ = type(self)
        return "%s(pk=%r, name=%r, set_product_advertisement_pk=%r)" % (
            class_.__name__,
            self.pk,
            self.description,
            self.set_product_advertisement_id,
        )
