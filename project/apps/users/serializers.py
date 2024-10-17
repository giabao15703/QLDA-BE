from apps.master_data.models import Promotion, PromotionUserUsed, PromotionTranslation
from apps.users.models import Supplier, SupplierCategory, Admin, UsersPermission, GroupPermission, BuyerActivity, Buyer, SupplierActivity
from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SupplierListSerializer(serializers.ModelSerializer):

    company_short_name = serializers.ReadOnlyField(source='supplier.company_short_name')
    company_long_name = serializers.ReadOnlyField(source='supplier.company_long_name')
    company_tax = serializers.ReadOnlyField(source='supplier.company_tax')
    company_logo = serializers.ImageField(source='supplier.company_logo')
    company_address = serializers.ReadOnlyField(source='supplier.company_address')
    company_city = serializers.ReadOnlyField(source='supplier.company_city')
    company_country = serializers.ReadOnlyField(source='supplier.company_country.id')
    company_country_state = serializers.ReadOnlyField(source='supplier.company_country_state.id')
    company_ceo_owner_name = serializers.ReadOnlyField(source='supplier.company_ceo_owner_name')
    company_ceo_owner_email = serializers.ReadOnlyField(source='supplier.company_ceo_owner_email')
    company_number_of_employee = serializers.ReadOnlyField(source='supplier.company_number_of_employee.id')
    company_website = serializers.ReadOnlyField(source='supplier.company_website')
    company_credential_profile = serializers.FileField(source='supplier.company_credential_profile')
    company_referral_code = serializers.ReadOnlyField(source='supplier.company_referral_code')

    gender = serializers.ReadOnlyField(source='supplier.gender.id')
    phone = serializers.ReadOnlyField(source='supplier.phone')
    position = serializers.ReadOnlyField(source='supplier.position.id')
    level = serializers.ReadOnlyField(source='supplier.level.id')

    bank_name = serializers.ReadOnlyField(source='supplier.bank_name')
    bank_code = serializers.ReadOnlyField(source='supplier.bank_code')
    bank_address = serializers.ReadOnlyField(source='supplier.bank_address')
    beneficiary_name = serializers.ReadOnlyField(source='supplier.beneficiary_name')
    switch_bic_code = serializers.ReadOnlyField(source='supplier.switch_bic_code')
    bank_account_number = serializers.ReadOnlyField(source='supplier.bank_account_number')
    bank_currency = serializers.ReadOnlyField(source='supplier.bank_currency.id')
    international_bank = serializers.ReadOnlyField(source='supplier.international_bank')
    company_full_name = serializers.ReadOnlyField(source='supplier.company_full_name')


    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'user_type',
            'first_name',
            'last_name',
            'company_short_name',
            'company_long_name',
            'company_tax',
            'company_logo',
            'company_address',
            'company_city',
            'company_country',
            'company_country_state',
            'company_ceo_owner_name',
            'company_ceo_owner_email',
            'company_number_of_employee',
            'company_website',
            'company_credential_profile',
            'company_referral_code',
            'gender',
            'phone',
            'position',
            'level',
            'bank_name',
            'bank_code',
            'bank_address',
            'beneficiary_name',
            'switch_bic_code',
            'bank_account_number',
            'bank_currency',
            'international_bank',
            'company_full_name',
        )


class BuyerSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    user_type = serializers.ReadOnlyField(source='user.user_type')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')

    class Meta:
        model = Buyer
        fields = ('id', 'username', 'email', 'user_type', 'first_name', 'last_name', 'company_full_name')


class SupplierCategorySerializer(serializers.ModelSerializer):
    user_supplier_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    class Meta:
        model = SupplierCategory
        fields = (
            'id',
            'category_id',
            'percentage',
            'minimum_of_value',
            'user_supplier_id',
        )


class AdminPermissionSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    short_name = serializers.ReadOnlyField(source='user.short_name')
    created = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    valid_from = serializers.SerializerMethodField()
    valid_to = serializers.SerializerMethodField()

    class Meta:
        model = UsersPermission
        fields = ('id', 'username', 'short_name', 'email', 'created', 'valid_from', 'valid_to', 'role', 'modules', 'status')

    def get_role(self, obj):
        permission = GroupPermission.objects.get(id=obj.permission_id)
        if permission.role == 1:
            return "Master"
        if permission.role == 2:
            return "A1"
        if permission.role == 3:
            return "A2"
        else:
            return "A3"

    def get_modules(self, obj):
        permission = GroupPermission.objects.select_related('group').get(id=obj.permission_id)
        return permission.group.name

    def get_status(self, obj):
        if obj.status == 1:
            return 'Active'
        if obj.status == 2:
            return 'Inactive'
        if obj.status == 3:
            return 'cancelled'
        if obj.status == 4:
            return 'pending'

    def get_created(self, obj):
        created = obj.user.created
        created = datetime.strftime(created, '%Y-%m-%d')
        return created

    def get_valid_from(self, obj):
        valid_from = obj.valid_from
        valid_from = datetime.strftime(valid_from, '%Y-%m-%d')
        return valid_from

    def get_valid_to(self, obj):
        valid_to = obj.valid_to
        valid_to = datetime.strftime(valid_to, '%Y-%m-%d')
        return valid_to


class BuyerExportSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    full_name = serializers.ReadOnlyField(source='user.full_name')
    created = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    valid_from = serializers.SerializerMethodField()
    valid_to = serializers.SerializerMethodField()
    profile_features = serializers.ReadOnlyField(source='profile_features.name')
    no_eauction_year = serializers.ReadOnlyField(source='profile_features.no_eauction_year')
    rfx_year = serializers.ReadOnlyField(source='profile_features.rfx_year')

    class Meta:
        model = Buyer
        fields = (
            'id',
            'username',
            'full_name',
            'email',
            'created',
            'valid_from',
            'valid_to',
            'status',
            'profile_features',
            'no_eauction_year',
            'rfx_year',
        )

    def get_status(self, obj):
        if obj.user.status == 1:
            return 'Active'
        if obj.user.status == 2:
            return 'Inactive'
        if obj.user.status == 3:
            return 'Cancelled'
        if obj.status == 4:
            return 'Pending'

    def get_created(self, obj):
        created = obj.user.created
        created = datetime.strftime(created, '%Y-%m-%d')
        return created

    def get_valid_from(self, obj):
        valid_from = obj.valid_from
        valid_from = datetime.strftime(valid_from, '%Y-%m-%d')
        return valid_from

    def get_valid_to(self, obj):
        valid_to = obj.valid_to
        valid_to = datetime.strftime(valid_to, '%Y-%m-%d')
        return valid_to


class BuyerActivitySerializer(serializers.ModelSerializer):
    changed_date = serializers.SerializerMethodField()
    changed_by = serializers.SerializerMethodField()

    class Meta:
        model = BuyerActivity
        fields = ('reason_manual', 'changed_by', 'changed_date')

    def get_changed_date(self, obj):
        changed_date = obj.changed_date
        changed_date = datetime.strftime(changed_date, '%Y-%m-%d')
        return changed_date

    def get_changed_by(self, obj):
        if obj.changed_by is not None:
            return obj.changed_by.username
        return "System"


class SupplierExportSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    created = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    valid_from = serializers.SerializerMethodField()
    valid_to = serializers.SerializerMethodField()
    profile_features = serializers.ReadOnlyField(source='profile_features.name')
    flash_sale = serializers.SerializerMethodField()
    report_year = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ('id', 'username', 'email', 'created', 'valid_from', 'valid_to', 'status', 'profile_features', 'report_year', 'flash_sale')

    def get_status(self, obj):
        if obj.user.status == 1:
            return 'Active'
        if obj.user.status == 2:
            return 'Inactive'
        if obj.user.status == 3:
            return 'Cancelled'
        if obj.status == 4:
            return 'Pending'

    def get_created(self, obj):
        created = obj.user.created
        created = datetime.strftime(created, '%Y-%m-%d')
        return created

    def get_valid_from(self, obj):
        valid_from = obj.valid_from
        valid_from = datetime.strftime(valid_from, '%Y-%m-%d')
        return valid_from

    def get_valid_to(self, obj):
        valid_to = obj.valid_to
        valid_to = datetime.strftime(valid_to, '%Y-%m-%d')
        return valid_to

    def get_flash_sale(self, obj):
        if obj.profile_features.flash_sale == 0:
            return "No"
        return obj.profile_features.flash_sale

    def get_report_year(self, obj):
        if obj.profile_features.report_year == 99999:
            return "All"
        return obj.profile_features.report_year


class SupplierActivitySerializer(serializers.ModelSerializer):
    changed_date = serializers.SerializerMethodField()
    changed_by = serializers.SerializerMethodField()

    class Meta:
        model = SupplierActivity
        fields = ('reason_manual', 'changed_by', 'changed_date')

    def get_changed_date(self, obj):
        changed_date = obj.changed_date
        changed_date = datetime.strftime(changed_date, '%Y-%m-%d')
        return changed_date

    def get_changed_by(self, obj):
        if obj.changed_by is not None:
            return obj.changed_by.username
        return "System"

class PromotionExportSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    discount = serializers.ReadOnlyField()
    valid_from = serializers.SerializerMethodField()
    valid_to = serializers.SerializerMethodField()
    status = serializers.BooleanField()
    apply_for_buyer = serializers.BooleanField()
    apply_for_supplier = serializers.BooleanField()
    visible = serializers.BooleanField()
    user_given = serializers.ReadOnlyField()
    user_given_email = serializers.ReadOnlyField()
    commission = serializers.ReadOnlyField()
    translated = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = (
            'id',
            'name', 
            'description', 
            'discount', 
            'valid_from', 
            'valid_to', 
            'status', 
            'apply_for_buyer', 
            'apply_for_supplier',
            'visible', 
            'user_given', 
            'user_given_email', 
            'commission',
            'translated',
        )

    def get_valid_from(self, obj):
        valid_from = obj.valid_from
        valid_from = datetime.strftime(valid_from, '%Y-%m-%d')
        return valid_from

    def get_valid_to(self, obj):
        valid_to = obj.valid_to
        valid_to = datetime.strftime(valid_to, '%Y-%m-%d')
        return valid_to

    def get_translated(self, obj):
        trans = PromotionTranslation.objects.filter(promotion=obj, language_code='vi').first()
        if trans is not None:
            return trans.description
        else:
            return None

class PromotionUserUsedExportSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='promotion.name')
    valid_from = serializers.SerializerMethodField()
    valid_to = serializers.SerializerMethodField()
    visible = serializers.BooleanField(source='promotion.visible')
    user_given = serializers.ReadOnlyField(source='promotion.user_given')
    user_given_email = serializers.ReadOnlyField(source='promotion.user_given_email')
    commission = serializers.ReadOnlyField(source='promotion.commission')
    status = serializers.BooleanField(source='promotion.status')
    discount = serializers.ReadOnlyField(source='promotion.discount')
    date_used = serializers.SerializerMethodField()

    class Meta:
        model = PromotionUserUsed
        fields = (
            'id',
            'title', 
            'user_used', 
            'user_used_email', 
            'user_name', 
            'date_used', 
            'real_amount', 
            'amount_after_discount',
            'name',
            'valid_from',
            'valid_to', 
            'visible', 
            'user_given', 
            'user_given_email', 
            'commission',
            'status',
            'discount', 
        )

    def get_valid_from(self, obj):
        promotion = Promotion.objects.filter(id=obj.promotion.id).first()
        valid_from = promotion.valid_from
        valid_from = datetime.strftime(valid_from, '%Y-%m-%d')
        return valid_from

    def get_valid_to(self, obj):
        promotion = Promotion.objects.filter(id=obj.promotion.id).first()
        valid_to = promotion.valid_to
        valid_to = datetime.strftime(valid_to, '%Y-%m-%d')
        return valid_to
    
    def get_date_used(self, obj):
        if obj.date_used is not None:
            date_used = obj.date_used
            date_used = datetime.strftime(date_used, '%Y-%m-%d')
            return date_used
        return None
