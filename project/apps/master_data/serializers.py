from rest_framework import serializers
from apps.master_data.models import Country, CountryState, Currency, ContractType
from apps.master_data.models import FamilyCode, ClusterCode, SubClusterCode, Category
from apps.master_data.models import PaymentTerm, DeliveryTerm, UnitofMeasure
from apps.master_data.models import EmailTemplates, NumberofEmployee, Gender
from apps.master_data.models import TechnicalWeighting, AuctionType, Position, Level

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'item_code', 'name', 'status']

class CountryStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryState
        fields = ['id', 'state_code', 'name', 'status', 'country_id']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'item_code', 'status']


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = ['id', 'name', 'status']


class FamilyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyCode
        fields = ['id', 'item_code', 'name', 'status']


class ClusterCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterCode
        fields = ['id', 'family_code', 'item_code', 'name', 'status']


class SubClusterCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubClusterCode
        fields = ['id', 'cluster_code', 'item_code', 'name', 'status']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'sub_cluster_code', 'item_code', 'name', 'status']

class PaymentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerm
        fields = ['id', 'name', 'status']

class DeliveryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTerm
        fields = ['id', 'name', 'status']

class UnitofMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitofMeasure
        fields = ['id', 'name', 'item_code', 'status']

class EmailTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplates
        fields = ['id', 'name', 'content', 'status']

class NumberofEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberofEmployee
        fields = ['id', 'name', 'status']

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name', 'status', 'status']

class TechnicalWeightingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalWeighting
        fields = ['id', 'name', 'status']

class AuctionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionType
        fields = ['id', 'name', 'status']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'status']

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'status']
