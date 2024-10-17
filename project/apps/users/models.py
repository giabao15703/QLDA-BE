import binascii
import os
import uuid

from apps.master_data.models import (
    Category,
    Country,
    CountryState,
    Currency,
    NumberofEmployee,
    Position,
    Level,
    ClientFocus,
    IndustrySubSectors,
    Language,
    Gender,
    Promotion,
    UnitofMeasure,
    PaymentTerm
)
from apps.sale_schema.models import (
    ProfileFeaturesBuyer,
    ProfileFeaturesSupplier,
    SICPRegistration
)

from datetime import datetime

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel

def flash_sale_directory_path(instance, filename):
    return os.path.join(str(instance.user_supplier.user.id), "{}.{}".format('flash_sale', filename.split('.')[-1]))

def company_logo_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('company_logo', filename.split('.')[-1]))

def picture_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('picture', filename.split('.')[-1]))

def banner_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('banner', filename.split('.')[-1]))

def company_credential_profile_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('company_credential_profile', filename.split('.')[-1]))

def supplier_form_registration_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('supplier_form_registration', filename.split('.')[-1]))

def bank_certification_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('bank_certification', filename.split('.')[-1]))

def quality_certification_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('quality_certification', filename.split('.')[-1]))

def business_license_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('business_license', filename.split('.')[-1]))

def tax_certification_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('tax_certification', filename.split('.')[-1]))

def one_year():
    return timezone.now() + timezone.timedelta(days=365)

def orthers_directory_path(instance, filename):
    return os.path.join(str(instance.user.id), "{}.{}".format('orthers', filename.split('.')[-1]))

def company_credential_profiles_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('company_credential_profile', filename.split('.')[-1]))

def supplier_form_registrations_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('supplier_form_registration', filename.split('.')[-1]))

def bank_certifications_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('bank_certification', filename.split('.')[-1]))

def quality_certifications_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('quality_certification', filename.split('.')[-1]))

def business_licenses_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('business_license', filename.split('.')[-1]))

def tax_certifications_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('tax_certification', filename.split('.')[-1]))

def others_directory_path(instance, filename):
    return os.path.join(str(instance.supplier.user.id), "{}.{}".format('orthers', filename.split('.')[-1]))

def products_directory_path(instance, filename):
    return os.path.join(str(instance.supplier_product.user_supplier.user.id), "{}.{}".format("product_image_" + slugify(instance.supplier_product.product_name) + "_" + str(uuid.uuid4()), filename.split(".")[-1]))

def supplier_certificate_path(instance, filename):
    return os.path.join(str(instance.user_supplier.user_id), "{}.{}".format(slugify(instance.user_supplier.user.full_name) + "_" + str(uuid.uuid4()), filename.split(".")[-1]))

GENDER_CHOICES = ((1, 'male'), (2, 'female'), (3, 'other'))

USER_TYPE_CHOICES = ((1, 'admin'), (2, 'buyer'), (3, 'supplier'))

PROFILE_FEATURES_CHOICES = (
    (1, 'basic'),
    (2, 'premium'),
    (3, 'sponsor'),
)

STATUS_CHOICES = ((1, 'active'), (2, 'inactive'), (3, 'deactive'))

ADMIN_ROLE_CHOICES = (
    (1, 'master'),
    (2, 'a1'),
    (3, 'a2'),
    (4, 'a3'),
)

PERMISSION_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'inactive'),
    (3, 'cancelled'),
    (4, 'pending'),
)

COMPANY_POSITION_CHOICES = (
    (1, 'owner'),
    (2, 'staff'),
)

DIAMOND_SPONSOR_STATUS_CHOICES = (
    (1, "active"),
    (2, "inactive"),
)

DIAMOND_SPONSOR_CONFIRM_CHOICES = (
    (1, "approved"),
    (2, "waiting"),
    (3, "reject"),
)

SICP_CONFIRM_CHOICES = (
    (1, "certified"),
    (2, "waiting"),
    (3, "failed"),
)

SICP_Review_CHOICES = (
    (1, "reviewed"),
    (2, "waiting review"),
)

SICP_USER_OR_ADMIN_CHOICES = (
    (1, "user"),
    (2, "admin_internal_document"),
    (3, "admin_external_document"),
)

SUPPLIER_FLASH_SALE_CONFIRM_CHOICES = (
    (1, "approved"),
    (2, "waiting"),
    (3, "rejected"),
)


SICP_TYPE_CHOICES = (
    (1, "bank_account"),
    (2, "certification_management"),
    (3, "due_diligence"),
    (4, "financial_risk_management"),
    (5, "legal_status"),
    (6, "document_internal"),
    (7, "document_external"),
    (8, "sanction_check"),
)

SICP_FILE_VERSION_CHOICES = (
    (1, "English"),
    (2, "Vietnamese"),
)

RATING_CHOICES = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)

class ProductType(models.TextChoices):
    PRODUCT = "product", _("Product")
    FLASH_SALE = "flash_sale", _("Flash_sale")

class ProductConfirmStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    APPROVED = "approved", _("Approved")
    WAITING = "waiting", _("Waiting")
    REJECTED = "rejected", _("Rejected")

class ProductInventoryStatus(models.TextChoices):
    STOCKING = "stocking", _("Stocking")
    OUT_OF_STOCK = "out_of_stock", _("Out_of_stock")

class SupplierCertificateType(models.TextChoices):
    PDF = "pdf", _("Pdf")
    CSV = "csv", _("Csv")
    DOC = "doc", _("Doc")
    IMAGE = "image", _("Image") 
    VIDEO = "video", _("Video")
    OTHER = "other", _("Other")

class UserFollowingSupplierStatus(models.TextChoices):
    FOLLOWING = "following", _("FOLLOWING")
    UN_FOLLOW = "un_follow", _("UN_FOLLOW")

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. ' 'Unselect this instead of deleting accounts.'),
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractUser, TimeStampedModel):
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    email = models.EmailField()
    activate_token = models.CharField(max_length=40)
    activate_time = models.DateTimeField(null=True)
    first_name = models.CharField(max_length=32, blank=True, null=True)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True, default=1)
    short_name = models.CharField(max_length=32, blank=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    local_time = models.CharField(max_length=32, default='Asia/Ho_Chi_Minh')
    company_position = models.PositiveSmallIntegerField(choices=COMPANY_POSITION_CHOICES, default=1)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, default=1)

    def get_profile(self):
        if self.isBuyer():
            profile = Buyer.objects.get(user_id=self.id)
        elif self.isSupplier():
            profile = Supplier.objects.get(user_id=self.id)
        elif self.isAdmin():
            profile = Buyer.objects.get(user_id=self.id)
        return profile

    def save(self, *args, **kwargs):
        if not self.id:
            self.activate_token = self.generate_key()

        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def isAdmin(self):
        return self.user_type == 1

    def isBuyer(self):
        return self.user_type == 2

    def isSupplier(self):
        return self.user_type == 3

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user_type', 'email'], name='user_type_email_unique')]
        db_table = 'users_user'


class Token(models.Model):
    """
    The default authorization token model.
    """

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_token', on_delete=models.CASCADE, verbose_name=_("User"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'users_token'


class ForgotPasswordToken(models.Model):
    """
    The default authorization token model.
    """

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_forgot_password_token', on_delete=models.CASCADE, verbose_name=_("User"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        db_table = 'users_forgot_password_token'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer')
    company_full_name = models.CharField(max_length=255, null=True, blank=True)
    company_short_name = models.CharField(max_length=32, null=True, blank=True)
    company_long_name = models.CharField(max_length=96, null=True, blank=True)
    company_logo = models.ImageField(upload_to=company_logo_directory_path, null=True, blank=True)
    company_tax = models.CharField(max_length=32)
    company_address = models.CharField(max_length=256)
    company_city = models.CharField(max_length=32)
    company_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    company_country_state = models.ForeignKey(CountryState, default=1, on_delete=models.CASCADE)
    company_number_of_employee = models.ForeignKey(NumberofEmployee, on_delete=models.CASCADE)
    company_website = models.CharField(max_length=32)
    company_referral_code = models.CharField(max_length=100, null=True, blank=True)
    company_email = models.CharField(max_length=32, null=True, blank=True)

    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_directory_path, null=True, blank=True)
    phone = models.CharField(max_length=32)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True, default=1)
    profile_features = models.ForeignKey(ProfileFeaturesBuyer, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True, blank=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(default=one_year)
    send_mail_30_day = models.DateTimeField(null=True, blank=True)
    send_mail_15_day = models.DateTimeField(null=True, blank=True)
    send_mail_7_day = models.DateTimeField(null=True, blank=True)
    send_mail_expire = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users_buyer'


class BuyerActivity(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='buyer_activity')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    reason_manual = models.CharField(max_length=256, null=True)
    changed_state = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        db_table = 'users_buyer_activity'


class BuyerSubAccounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_sub_accounts')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='buyer')
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, default=1)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_directory_path, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'users_buyer_sub_accounts'


class BuyerSubAccountsActivity(models.Model):
    buyer_sub_accounts = models.ForeignKey(BuyerSubAccounts, on_delete=models.CASCADE, related_name='buyer_sub_accounts_activity')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    reason_manual = models.CharField(max_length=256, null=True)
    changed_state = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        db_table = 'users_buyer_sub_accounts_activity'

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier')
    company_full_name = models.CharField(max_length=255, null=True, blank=True)
    company_short_name = models.CharField(max_length=32, null=True, blank=True)
    company_long_name = models.CharField(max_length=96, null=True, blank=True)
    company_tax = models.CharField(max_length=32)
    company_logo = models.ImageField(upload_to=company_logo_directory_path, null=True, blank=True)
    company_address = models.CharField(max_length=256)
    company_city = models.CharField(max_length=32)
    company_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    company_country_state = models.ForeignKey(CountryState, default=1, on_delete=models.CASCADE)
    company_ceo_owner_name = models.CharField(max_length=32, blank=True, null=True)
    company_ceo_owner_email = models.CharField(max_length=32, blank=True, null=True)
    company_number_of_employee = models.ForeignKey(NumberofEmployee, on_delete=models.CASCADE)
    company_website = models.CharField(max_length=32, blank=True, null=True)
    company_credential_profile = models.FileField(upload_to=company_credential_profile_directory_path, null=True, blank=True)
    company_referral_code = models.CharField(max_length=100, blank=True, null=True)
    company_tag_line = models.CharField(max_length=350, blank=True, null=True)
    company_description = models.CharField(max_length=350, null=True, blank=True)
    company_established_since = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)], null=True, blank=True
    )
    company_anniversary_date = models.DateTimeField(null=True, blank=True)

    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    picture = models.ImageField(upload_to=picture_directory_path, null=True, blank=True)
    image_banner = models.ImageField(upload_to=banner_directory_path, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True, default=1)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, related_name='currency', blank=True)

    bank_name = models.CharField(max_length=250, null=True, blank=True)
    bank_code = models.CharField(max_length=32, null=True, blank=True)
    bank_address = models.CharField(max_length=250, null=True, blank=True)
    beneficiary_name = models.CharField(max_length=250, null=True, blank=True)
    switch_bic_code = models.CharField(max_length=32, null=True, blank=True)
    bank_account_number = models.CharField(max_length=32, null=True, blank=True)
    bank_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='bank_currency', null=True, blank=True)
    international_bank = models.CharField(max_length=32, blank=True, null=True)

    supplier_form_registration = models.FileField(upload_to=supplier_form_registration_directory_path, null=True, blank=True)
    bank_certification = models.FileField(upload_to=bank_certification_directory_path, null=True, blank=True)
    quality_certification = models.FileField(upload_to=quality_certification_directory_path, null=True, blank=True)
    business_license = models.FileField(upload_to=business_license_directory_path, null=True, blank=True)
    tax_certification = models.FileField(upload_to=tax_certification_directory_path, null=True, blank=True)
    others = models.FileField(upload_to=orthers_directory_path, null=True, blank=True)
    profile_features = models.ForeignKey(ProfileFeaturesSupplier, on_delete=models.CASCADE, null=True)
    sicp_registration = models.ForeignKey(SICPRegistration, on_delete=models.CASCADE, null=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True, blank=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(default=one_year)
    send_mail_30_day = models.DateTimeField(null=True, blank=True)
    send_mail_15_day = models.DateTimeField(null=True, blank=True)
    send_mail_7_day = models.DateTimeField(null=True, blank=True)
    send_mail_expire = models.DateTimeField(null=True, blank=True)
    viewed = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    class Meta:
        db_table = 'users_supplier'


class SupplierActivity(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_activity')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    reason_manual = models.CharField(max_length=256, null=True)
    changed_state = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        db_table = 'users_supplier_activity'


class SupplierCompanyCredential(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_company_credential')
    company_credential_profile = models.FileField(upload_to=company_credential_profiles_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_company_credential'


class SupplierFormRegistrations(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_form_registrations')
    form_registration = models.FileField(upload_to=supplier_form_registrations_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_form_registration'


class SupplierBankCertification(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_bank_certification')
    bank_certification = models.FileField(upload_to=bank_certifications_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_bank_certification'


class SupplierQualityCertification(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_quality_certification')
    quality_certification = models.FileField(upload_to=quality_certifications_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_quality_certification'


class SupplierBusinessLicense(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_business_license')
    business_license = models.FileField(upload_to=business_licenses_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_business_license'


class SupplierTaxCertification(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_tax_certification')
    tax_certification = models.FileField(upload_to=tax_certifications_directory_path, null=True)

    class Meta:
        db_table = 'users_supplier_tax_certification'


class SupplierOthers(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_other')
    other = models.FileField(upload_to=others_directory_path, null=True, blank=True)

    class Meta:
        db_table = 'users_supplier_others'


class SupplierCategory(models.Model):
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) # default related_name: suppliercategory_set
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    percentage = models.FloatField()
    minimum_of_value = models.FloatField()

    class Meta:
        db_table = 'users_supplier_category'


class SupplierIndustry(models.Model):
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    industry_sub_sectors = models.ForeignKey(IndustrySubSectors, on_delete=models.CASCADE)
    percentage = models.FloatField()

    class Meta:
        db_table = 'users_supplier_industry'


class SupplierClientFocus(models.Model):
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    client_focus = models.ForeignKey(ClientFocus, on_delete=models.CASCADE)
    percentage = models.FloatField()

    class Meta:
        db_table = 'users_supplier_client_focus'


class SupplierFlashSale(models.Model):
    sku_number = models.CharField(max_length=32)
    description = models.TextField(max_length=2048, default='')
    picture = models.ImageField(upload_to=flash_sale_directory_path, null=True)
    initial_price = models.FloatField()
    percentage = models.FloatField()
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.PositiveSmallIntegerField(choices=SUPPLIER_FLASH_SALE_CONFIRM_CHOICES, default=2)
    re_order = models.IntegerField(default=0, null=True)
    text_editer = models.CharField(max_length=10000, null=True)
    url_path = models.CharField(max_length=200, null=True, blank=True)
    reach_number = models.IntegerField(default=0)
    click_number = models.IntegerField(default=0)

    class Meta:
        db_table = 'users_supplier_flash_sale'
        unique_together = ('sku_number', 'user_supplier',)


def portfolio_image_directory_path(instance, filename):
    return os.path.join(str('supplier_portfolio'), "{}.{}".format('supplier_portfolio', filename.split('.')[-1]))


class SupplierPortfolio(models.Model):
    company = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)
    value = models.FloatField()
    project_description = models.CharField(max_length=2048)
    image = models.ImageField(upload_to=portfolio_image_directory_path, null=True)
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_portfolio')

    class Meta:
        db_table = 'users_supplier_portfolio'


class BuyerIndustry(models.Model):
    user_buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='buyer_industry')
    industry = models.ForeignKey(IndustrySubSectors, on_delete=models.CASCADE, related_name='buyer_industry')

    class Meta:
        db_table: 'users_buyer_industry'


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    long_name = models.CharField(max_length=96)
    picture = models.ImageField(upload_to=picture_directory_path, null=True)

    class Meta:
        db_table = 'users_admin'


class GroupPermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    role = models.PositiveSmallIntegerField(choices=ADMIN_ROLE_CHOICES)

    class Meta:
        db_table = 'users_groups_permission'


class UsersPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(GroupPermission, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    status = models.IntegerField(choices=PERMISSION_STATUS_CHOICES)

    class Meta:
        db_table = 'users_user_permission'


class UserSubstitutionPermission(models.Model):
    user_permission = models.ForeignKey(UsersPermission, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=PERMISSION_STATUS_CHOICES)

    class Meta:
        db_table = 'users_substitution_permission'


class SupplierSubAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_sub_account')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier')
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, default=1)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=picture_directory_path, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'users_supplier_sub_account'


class SupplierSubAccountActivity(models.Model):
    supplier_sub_account = models.ForeignKey(SupplierSubAccount, on_delete=models.CASCADE, related_name='supplier_sub_accounts_activity')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    reason_manual = models.CharField(max_length=256, null=True)
    changed_state = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        db_table = 'users_supplier_sub_account_activity'

def diamond_sponsor_directory_path(instance, filename):
    return os.path.join(str("diamond_sponsor"), "{}.{}".format("diamond_sponsor", filename.split(".")[-1]))

class UserDiamondSponsor(models.Model):
    image = models.ImageField(upload_to=diamond_sponsor_directory_path)
    product_name = models.CharField(max_length=255, null=True, blank= True)
    description = models.CharField(max_length=255, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_diamond_sponsors")
    status = models.PositiveSmallIntegerField(choices=DIAMOND_SPONSOR_STATUS_CHOICES)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.PositiveSmallIntegerField(choices=DIAMOND_SPONSOR_CONFIRM_CHOICES)
    text_editer = models.CharField(max_length=10000, null=True)
    reach_number = models.IntegerField(default=0)
    click_number = models.IntegerField(default=0)
    reach_number_count = models.IntegerField(default=0)

    class Meta:
        db_table = "users_user_diamond_sponsor"

def sicp_file_path(instance, filename):
    return os.path.join(str("sicp_file"), "{}.{}".format("sicp_file", filename.split(".")[-1]))

def sicp_text_editor_file_path(instance, filename):
    return os.path.join(str("sicp_text_editor_file"), "{}.{}".format("sicp_text_editor_file", filename.split(".")[-1]))

class SupplierSICP(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_sicps")
    sanction_check = models.CharField(max_length=255, null=True)
    is_confirmed = models.PositiveSmallIntegerField(choices=SICP_CONFIRM_CHOICES)
    is_reviewed = models.PositiveSmallIntegerField(choices=SICP_Review_CHOICES)  
    created_date = models.DateTimeField(null=True, blank=True)
    expired_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "supplier_sicp"

class SupplierSICPFile(models.Model):
    file_name = models.FileField(upload_to=sicp_file_path)
    sicp_type = models.PositiveSmallIntegerField(choices=SICP_TYPE_CHOICES)
    sicp = models.ForeignKey(SupplierSICP, on_delete=models.CASCADE, related_name="sicp_files")
    ordered = models.IntegerField(null=True)
    user_or_admin = models.PositiveSmallIntegerField(choices=SICP_USER_OR_ADMIN_CHOICES, null=True)

    class Meta:
        db_table = "supplier_sicp_files"

class SICPTextEditor(models.Model):
    text_editer_en = models.CharField(max_length=10000, null=True, blank=True)
    text_editer_vi = models.CharField(max_length=10000, null=True, blank=True)
    sicp_type = models.PositiveSmallIntegerField(choices=SICP_TYPE_CHOICES)

    class Meta:
        db_table = "supplier_sicp_text_editor"

class SICPTextEditorFile(models.Model):
    file_name = models.FileField(upload_to=sicp_text_editor_file_path, null=True, blank=True)
    sicp_text_editor = models.ForeignKey(SICPTextEditor, on_delete=models.CASCADE, related_name="sicp_text_editor_files")
    file_version = models.PositiveSmallIntegerField(choices=SICP_FILE_VERSION_CHOICES, null=True, blank=True)

    class Meta:
        db_table = "supplier_sicp_text_editor_file"

class UserDiamondSponsorFee(models.Model):
    title = models.CharField(max_length=255)
    fee = models.FloatField()

    class Meta:
        db_table = 'users_user_diamond_sponsor_fee'

class SupplierProduct(models.Model):
    discount_program_form = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=32)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='product_country')
    state = models.ForeignKey(CountryState, on_delete=models.CASCADE, related_name='product_state')
    regular_product = models.BooleanField(default=True)
    green_product = models.BooleanField(default=False)
    official_product = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    sku_number = models.CharField(max_length=32, null=True, blank=True)
    description = models.TextField(max_length=2048, default='')
    type = models.CharField(max_length=32, choices=ProductType.choices, default=ProductType.PRODUCT)
    product_name = models.CharField(max_length=1000, null=True, blank=True)
    unit_of_measure = models.ForeignKey(UnitofMeasure, on_delete=models.SET_NULL, related_name="supplier_products", null=True, blank=True)
    is_visibility = models.BooleanField(default=True)
    confirmed_status = models.CharField(max_length=32, choices=ProductConfirmStatus.choices, default=ProductConfirmStatus.WAITING, null=True, blank=True)
    specification = models.CharField(max_length=100000, null=True, blank=True)
    minimum_order_quantity = models.CharField(max_length=100, null=True, blank=True)
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_products")
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.SET_NULL, related_name="supplier_products", null=True, blank=True)
    inventory_status = models.CharField(max_length=32, choices=ProductInventoryStatus.choices, default=ProductInventoryStatus.STOCKING, null=True, blank=True)
    provide_ability = models.CharField(max_length=255, null=True, blank=True)
    support = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    origin_of_production = models.CharField(max_length=255, null=True, blank=True)
    origin_of_production_country = models.ForeignKey(Country, on_delete=models.SET_NULL, related_name="supplier_products", null=True, blank=True)
    guarantee = models.CharField(max_length=255, null=True, blank=True)
    other_information = models.CharField(max_length=100000, null=True, blank=True)
    reach_number = models.IntegerField(default=0)
    click_number = models.IntegerField(default=0)
    url_path = models.CharField(max_length=200, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    create_date = models.DateField(null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=16, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'users_supplier_product'
        unique_together = ('sku_number', 'user_supplier',)

class SupplierProductImage(models.Model):
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to=products_directory_path, max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'users_supplier_product_image'
        
class SupplierProductFlashSale(models.Model):
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="product_flash_sales")
    initial_price = models.FloatField(null=True, blank=True)
    discounted_price = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'users_supplier_product_flash_sale'

class SupplierProductWholesalePrice(models.Model):
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="product_wholesale_price_list")
    quality_from = models.FloatField(null=True, blank=True)
    quality_to = models.FloatField(null=True, blank=True)
    price_bracket = models.FloatField(null=True, blank=True)
    delivery_days = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'users_supplier_product_wholesale_price'

class RelatedSupplierProduct(models.Model):
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="related_supplier_product_product")
    related_supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="related_supplier_product_related_product")

    class Meta:
        db_table = 'users_supplier_related_supplier_product'
    
class SupplierCertificate(TimeStampedModel):
    user_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="certificate")
    file = models.FileField(upload_to=supplier_certificate_path, max_length=500)
    name = models.CharField(max_length=500, null=True, blank=True)
    type = models.CharField(max_length=100, choices=SupplierCertificateType.choices, null=True, blank=True)
    size = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'users_supplier_certificate'    

class SupplierProductCategory(models.Model):
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="supplier_product_category_list")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="supplier_product_category_list")

    class Meta:
        db_table = 'users_supplier_supplier_product_category'
        unique_together = ('category', 'supplier_product',)

class UserFollowingSupplier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_following_supplier')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='user_supplier')
    follow_status = models.CharField(max_length=32, choices=UserFollowingSupplierStatus.choices, default=UserFollowingSupplierStatus.UN_FOLLOW)
    class Meta:
        db_table = 'users_following_supplier'
        unique_together = ('user', 'supplier',)

class UserRatingSupplierProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rating_supplier_product')
    supplier_product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, related_name="supplier_product")
    quality_rating = models.IntegerField(default=0, validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])
    delivery_time_rating = models.IntegerField(default=0, validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])
    class Meta:
        db_table = 'users_rating_supplier_product'
        unique_together = ('user', 'supplier_product',)