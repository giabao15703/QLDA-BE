from apps.users.models import Buyer, Supplier
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'user_type', 'email', 'first_name', 'last_name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            user_type=validated_data['user_type'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class BuyerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Buyer
        fields = (
            'id',
            'company_email',
            'company_short_name',
            'company_long_name',
            'company_logo',
            'company_tax',
            'company_address',
            'company_city',
            'company_country',
            'company_country_state',
            'company_number_of_employee',
            'company_website',
            'company_referral_code',
            'gender',
            'picture',
            'phone',
            'position',
            'level',
            'user_id'
        )


class SupplierSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Supplier
        fields = (
            'id',
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
            'supplier_form_registration',
            'bank_certification',
            'quality_certification',
            'business_license',
            'tax_certification',
            'user_id',
        
        )
