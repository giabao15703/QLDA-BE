# Create your views here.
import csv
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from typing import List

from apps.master_data.models import Country, Currency, ContractType, CountryState, SubClusterCodeTranslation, ClusterCodeTranslation, FamilyCodeTranslation, CategoryTranslation
from apps.master_data.serializers import CountrySerializer, CurrencySerializer, ContractTypeSerializer, CountryStateSerializer
from apps.master_data.models import FamilyCode, ClusterCode, SubClusterCode, Category
from apps.master_data.serializers import FamilyCodeSerializer, ClusterCodeSerializer, SubClusterCodeSerializer, CategorySerializer
from apps.master_data.models import PaymentTerm, DeliveryTerm, UnitofMeasure
from apps.master_data.serializers import PaymentTermSerializer, DeliveryTermSerializer, UnitofMeasureSerializer
from apps.master_data.models import EmailTemplates, NumberofEmployee, Gender
from apps.master_data.serializers import EmailTemplatesSerializer, NumberofEmployeeSerializer, GenderSerializer
from apps.master_data.models import TechnicalWeighting, AuctionType
from apps.master_data.serializers import TechnicalWeightingSerializer, AuctionTypeSerializer
from apps.master_data.models import Position, Level
from apps.master_data.serializers import PositionSerializer, LevelSerializer

from django.http import Http404, HttpResponse
from django.db.models import Q, OuterRef, Subquery

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters


# ---------------API-Country-1st-----------------
class CountryList(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = CountrySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = Country.objects.filter(status=True)
        return queryset


class CountryDetail(APIView):
    def get_object(self, pk):
        try:
            return Country.objects.get(pk=pk)
        except Country.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        country = self.get_object(pk)
        serializer = CountrySerializer(country)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        country = self.get_object(pk)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        country = self.get_object(pk)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CountryStateList(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = CountryStateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['state_code', 'name', 'status']

    def get_queryset(self):
        queryset = CountryState.objects.filter(status=True)
        return queryset


class CountryStateDetail(APIView):
    def get_object(self, pk):
        try:
            return CountryState.objects.get(pk=pk)
        except CountryState.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        country_state = self.get_object(pk)
        serializer = CountryStateSerializer(country_state)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        country_state = self.get_object(pk)
        serializer = CountryStateSerializer(country_state, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        country_state = self.get_object(pk)
        country_state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------API-Currency-2nd----------------------
class CurrencyList(generics.ListAPIView):
    pagination_class = None
    serializer_class = CurrencySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = Currency.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyDetail(APIView):
    def get_object(self, pk):
        try:
            return Currency.objects.get(pk=pk)
        except Currency.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        currency = self.get_object(pk)
        serializer = CurrencySerializer(currency)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        currency = self.get_object(pk)
        serializer = CurrencySerializer(currency, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        currency = self.get_object(pk)
        currency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------API-FamilyCode-3rd--------------------
class FamilyCodeList(generics.ListAPIView):
    pagination_class = None
    serializer_class = FamilyCodeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = FamilyCode.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = FamilyCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FamilyCodeDetail(APIView):
    def get_object(self, pk):
        try:
            return FamilyCode.objects.get(pk=pk)
        except FamilyCode.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        familyCode = self.get_object(pk)
        serializer = FamilyCodeSerializer(familyCode)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        familyCode = self.get_object(pk)
        serializer = FamilyCodeSerializer(familyCode, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        familyCode = self.get_object(pk)
        familyCode.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------API-ClusterCode-4th--------------------
class ClusterCodeList(generics.ListAPIView):
    pagination_class = None
    serializer_class = ClusterCodeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = ClusterCode.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = ClusterCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClusterCodeDetail(APIView):
    def get_object(self, pk):
        try:
            return ClusterCode.objects.get(pk=pk)
        except ClusterCode.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        clusterCode = self.get_object(pk)
        serializer = ClusterCodeSerializer(clusterCode)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        clusterCode = self.get_object(pk)
        serializer = ClusterCodeSerializer(clusterCode, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        clusterCode = self.get_object(pk)
        clusterCode.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------API-SubClusterCode-5th--------------------
class SubClusterCodeList(generics.ListAPIView):
    pagination_class = None
    serializer_class = SubClusterCodeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = SubClusterCode.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = SubClusterCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubClusterCodeDetail(APIView):
    def get_object(self, pk):
        try:
            return SubClusterCode.objects.get(pk=pk)
        except SubClusterCode.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        subClusterCode = self.get_object(pk)
        serializer = SubClusterCodeSerializer(subClusterCode)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        subClusterCode = self.get_object(pk)
        serializer = SubClusterCodeSerializer(subClusterCode, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        subClusterCode = self.get_object(pk)
        subClusterCode.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------API-Category-6th--------------------
class CategoryList(generics.ListAPIView):
    pagination_class = None
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = Category.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------API-ContractType-7th---------------------
class ContractTypeList(generics.ListAPIView):
    pagination_class = None
    serializer_class = ContractTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = ContractType.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = ContractTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractTypeDetail(APIView):
    def get_object(self, pk):
        try:
            return ContractType.objects.get(pk=pk)
        except ContractType.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        contracttype = self.get_object(pk)
        serializer = ContractTypeSerializer(contracttype)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        contracttype = self.get_object(pk)
        serializer = ContractTypeSerializer(contracttype, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        contracttype = self.get_object(pk)
        contracttype.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------API-PaymentTerm-8th---------------------
class PaymentTermList(generics.ListAPIView):
    pagination_class = None
    serializer_class = PaymentTermSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = PaymentTerm.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = PaymentTermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentTermDetail(APIView):
    def get_object(self, pk):
        try:
            return PaymentTerm.objects.get(pk=pk)
        except PaymentTerm.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        paymentterm = self.get_object(pk)
        serializer = PaymentTermSerializer(paymentterm)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        paymentterm = self.get_object(pk)
        serializer = PaymentTermSerializer(paymentterm, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        paymentterm = self.get_object(pk)
        paymentterm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------API-DeliveryTerm-9th---------------------
class DeliveryTermList(generics.ListAPIView):
    pagination_class = None
    serializer_class = DeliveryTermSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = DeliveryTerm.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = DeliveryTermSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryTermDetail(APIView):
    def get_object(self, pk):
        try:
            return DeliveryTerm.objects.get(pk=pk)
        except DeliveryTerm.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        deliveryterm = self.get_object(pk)
        serializer = DeliveryTermSerializer(deliveryterm)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        deliveryterm = self.get_object(pk)
        serializer = DeliveryTermSerializer(deliveryterm, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        deliveryterm = self.get_object(pk)
        deliveryterm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------API-UnitofMeasure-10th----------------------
class UnitofMeasureList(generics.ListAPIView):
    pagination_class = None
    serializer_class = UnitofMeasureSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['item_code', 'name', 'status']

    def get_queryset(self):
        queryset = UnitofMeasure.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = UnitofMeasureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnitofMeasureDetail(APIView):
    def get_object(self, pk):
        try:
            return UnitofMeasure.objects.get(pk=pk)
        except UnitofMeasure.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        unitofmeasure = self.get_object(pk)
        serializer = UnitofMeasureSerializer(unitofmeasure)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        unitofmeasure = self.get_object(pk)
        serializer = UnitofMeasureSerializer(unitofmeasure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        unitofmeasure = self.get_object(pk)
        unitofmeasure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------API-EmailTemplates-11th----------------------
class EmailTemplatesList(generics.ListAPIView):
    pagination_class = None
    serializer_class = EmailTemplatesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'content', 'status']

    def get_queryset(self):
        queryset = EmailTemplates.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = EmailTemplatesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailTemplatesDetail(APIView):
    def get_object(self, pk):
        try:
            return EmailTemplates.objects.get(pk=pk)
        except EmailTemplates.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        emailtemplates = self.get_object(pk)
        serializer = EmailTemplatesSerializer(emailtemplates)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        emailtemplates = self.get_object(pk)
        serializer = EmailTemplatesSerializer(emailtemplates, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        emailtemplates = self.get_object(pk)
        emailtemplates.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------API-NumberofEmployee-12th----------------------
class NumberofEmployeeList(generics.ListAPIView):
    pagination_class = None
    serializer_class = NumberofEmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'content', 'status']

    def get_queryset(self):
        queryset = NumberofEmployee.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = NumberofEmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NumberofEmployeeDetail(APIView):
    def get_object(self, pk):
        try:
            return NumberofEmployee.objects.get(pk=pk)
        except NumberofEmployee.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        numberofemployee = self.get_object(pk)
        serializer = NumberofEmployeeSerializer(numberofemployee)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        numberofemployee = self.get_object(pk)
        serializer = NumberofEmployeeSerializer(numberofemployee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        numberofemployee = self.get_object(pk)
        numberofemployee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------API-Gender-13th----------------------
class GenderList(generics.ListAPIView):
    pagination_class = None
    serializer_class = GenderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = Gender.objects.filter(status=True)
        return queryset

    def post(self, request, format=None):
        serializer = GenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenderDetail(APIView):
    def get_object(self, pk):
        try:
            return Gender.objects.get(pk=pk)
        except Gender.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        gender = self.get_object(pk)
        serializer = GenderSerializer(gender)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        gender = self.get_object(pk)
        serializer = GenderSerializer(gender, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        gender = self.get_object(pk)
        gender.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TechnicalWeightingList(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = TechnicalWeightingSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = TechnicalWeighting.objects.filter(status=True)
        return queryset


class AuctionTypeList(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = AuctionTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = AuctionType.objects.filter(status=True)
        return queryset


class PositionView(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = PositionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = Position.objects.filter(status=True)
        return queryset


class PositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    pagination_class = None
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class LevelView(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = LevelSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'status']

    def get_queryset(self):
        queryset = Level.objects.filter(status=True)
        return queryset


class LevelDetailView(generics.RetrieveUpdateDestroyAPIView):
    pagination_class = None
    queryset = Level.objects.all()
    serializer_class = LevelSerializer


class ExportMasterDataCCCFamilyCode(APIView):
    def post(self, request, format=None):
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            name = request.data.get('searchName')
            code = request.data.get('searchCode')

            filter_query = Q()
            if name is not None and len(name) > 0:
                filter_query.add(Q(name__icontains=name) | Q(name_en__icontains=name) | Q(name_vi__icontains=name), Q.AND)
            if code is not None and len(code) > 0:
                filter_query.add(Q(item_code=code), Q.AND)

            qs_family_name_en = FamilyCodeTranslation.objects.filter(language_code='en', family_code=OuterRef('pk'))
            qs_family_name_vi = FamilyCodeTranslation.objects.filter(language_code='vi', family_code=OuterRef('pk'))

            family_codes = FamilyCode.objects.annotate(
                name_en=Subquery(qs_family_name_en.values('name')),
                name_vi=Subquery(qs_family_name_vi.values('name'))
            ).filter(filter_query).order_by('id')

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="master_data_ccc_family_codes.csv"'

            writer = csv.DictWriter(
                response,
                fieldnames=[
                    'Code',
                    'Name of family code (en)',
                    'Name of family code (vi)',
                    'Status'
                ],
            )

            writer.writerow({
                'Code': 'Master Data/CCC Family Code',
            })

            writer.writeheader()

            for family_code in family_codes:
                writer.writerow(
                    {
                        'Code': family_code.item_code,
                        'Name of family code (en)': family_code.name_en,
                        'Name of family code (vi)': family_code.name_vi,
                        'Status': "Active" if family_code.status else "Inactive",
                    }
                )

            return response
        else:
            return Response(status=401)


class ExportMasterDataCCCClusterCode(APIView):
    def post(self, request, format=None):
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            name = request.data.get('searchName')
            code = request.data.get('searchCode')

            filter_query = Q()
            if name is not None and len(name) > 0:
                filter_query.add(Q(name__icontains=name) | Q(name_en__icontains=name) | Q(name_vi__icontains=name), Q.AND)
            if code is not None and len(code) > 0:
                filter_query.add(Q(item_code=code), Q.AND)

            qs_cluster_name_en = ClusterCodeTranslation.objects.filter(language_code='en', cluster_code=OuterRef('pk'))
            qs_cluster_name_vi = ClusterCodeTranslation.objects.filter(language_code='vi', cluster_code=OuterRef('pk'))
            cluster_codes = ClusterCode.objects.annotate(
                name_en=Subquery(qs_cluster_name_en.values('name')),
                name_vi=Subquery(qs_cluster_name_vi.values('name'))
            ).filter(filter_query).order_by('id')

            qs_family_name_en = FamilyCodeTranslation.objects.filter(language_code='en', family_code=OuterRef('pk'))
            qs_family_name_vi = FamilyCodeTranslation.objects.filter(language_code='vi', family_code=OuterRef('pk'))
            family_codes = FamilyCode.objects.annotate(
                name_en=Subquery(qs_family_name_en.values('name')),
                name_vi=Subquery(qs_family_name_vi.values('name'))
            ).filter(id__in=cluster_codes.values_list('family_code_id', flat=True))
            family_code_dict = dict((o.id, o) for o in family_codes)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="master_data_ccc_cluster_codes.csv"'

            writer = csv.DictWriter(
                response,
                fieldnames=[
                    'Code',
                    'Name of cluster code (en)',
                    'Name of cluster code (vi)',
                    'Status',
                    'Family code',
                    'Name of family code (en)',
                    'Name of family code (vi)',
                ],
            )

            writer.writerow({
                'Code': 'Master Data/CCC Cluster Code',
            })

            writer.writeheader()

            for cluster_code in cluster_codes:
                family_code = family_code_dict.get(cluster_code.family_code_id)
                if family_code is None:
                    continue

                writer.writerow(
                    {
                        'Code': cluster_code.item_code,
                        'Name of cluster code (en)': cluster_code.name_en,
                        'Name of cluster code (vi)': cluster_code.name_vi,
                        'Status': "Active" if cluster_code.status else "Inactive",
                        'Family code': family_code.item_code,
                        'Name of family code (en)': family_code.name_en,
                        'Name of family code (vi)': family_code.name_vi,
                    }
                )

            return response
        else:
            return Response(status=401)


class ExportMasterDataCCCSubClusterCode(APIView):
    def post(self, request, format=None):
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            name = request.data.get('searchName')
            code = request.data.get('searchCode')

            filter_query = Q()
            if name is not None and len(name) > 0:
                filter_query.add(Q(name__icontains=name) | Q(name_en__icontains=name) | Q(name_vi__icontains=name), Q.AND)
            if code is not None and len(code) > 0:
                filter_query.add(Q(item_code=code), Q.AND)

            qs_sub_cluster_name_en = SubClusterCodeTranslation.objects.filter(language_code='en', sub_cluster_code=OuterRef('pk'))
            qs_sub_cluster_name_vi = SubClusterCodeTranslation.objects.filter(language_code='vi', sub_cluster_code=OuterRef('pk'))
            sub_cluster_codes = SubClusterCode.objects.annotate(
                name_en=Subquery(qs_sub_cluster_name_en.values('name')),
                name_vi=Subquery(qs_sub_cluster_name_vi.values('name'))
            ).filter(filter_query).order_by('id')

            qs_cluster_code_name_en = ClusterCodeTranslation.objects.filter(language_code='en', cluster_code=OuterRef('pk'))
            qs_cluster_code_name_vi = ClusterCodeTranslation.objects.filter(language_code='vi', cluster_code=OuterRef('pk'))
            cluster_codes = ClusterCode.objects.annotate(
                name_en=Subquery(qs_cluster_code_name_en.values('name')),
                name_vi=Subquery(qs_cluster_code_name_vi.values('name'))
            ).filter(id__in=sub_cluster_codes.values_list('cluster_code_id', flat=True))
            cluster_code_dict = dict((o.id, o) for o in cluster_codes)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="master_data_ccc_sub_cluster_codes.csv"'

            writer = csv.DictWriter(
                response,
                fieldnames=[
                    'Code',
                    'Name of sub cluster code (en)',
                    'Name of sub cluster code (vi)',
                    'Status',
                    'Cluster code',
                    'Name of cluster code (en)',
                    'Name of cluster code (vi)',
                ],
            )

            writer.writerow({
                'Code': 'Master Data/CCC Sub Cluster Code',
            })

            writer.writeheader()

            for sub_cluster_code in sub_cluster_codes:
                cluster_code = cluster_code_dict.get(sub_cluster_code.cluster_code_id)
                if cluster_code is None:
                    continue

                writer.writerow(
                    {
                        'Code': sub_cluster_code.item_code,
                        'Name of sub cluster code (en)': sub_cluster_code.name_en,
                        'Name of sub cluster code (vi)': sub_cluster_code.name_vi,
                        'Status': "Active" if sub_cluster_code.status else "Inactive",
                        'Cluster code': cluster_code.item_code,
                        'Name of cluster code (en)': cluster_code.name_en,
                        'Name of cluster code (vi)': cluster_code.name_vi,
                    }
                )

            return response
        else:
            return Response(status=401)


class ExportMasterDataCCCCategory(APIView):
    def post(self, request, format=None):
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            name = request.data.get('searchName')
            code = request.data.get('searchCode')

            filter_query = Q()
            if name is not None and len(name) > 0:
                filter_query.add(Q(name__icontains=name) | Q(name_en__icontains=name) | Q(name_vi__icontains=name), Q.AND)
            if code is not None and len(code) > 0:
                filter_query.add(Q(item_code=code), Q.AND)

            qs_category_name_en = CategoryTranslation.objects.filter(language_code='en', category=OuterRef('pk'))
            qs_category_name_vi = CategoryTranslation.objects.filter(language_code='vi', category=OuterRef('pk'))
            categories = Category.objects.annotate(
                name_en=Subquery(qs_category_name_en.values('name')),
                name_vi=Subquery(qs_category_name_vi.values('name'))
            ).filter(filter_query).order_by('id')

            qs_sub_cluster_code_name_en = SubClusterCodeTranslation.objects.filter(language_code='en', sub_cluster_code=OuterRef('pk'))
            qs_sub_cluster_code_name_vi = SubClusterCodeTranslation.objects.filter(language_code='vi', sub_cluster_code=OuterRef('pk'))
            sub_cluster_codes = SubClusterCode.objects.annotate(
                name_en=Subquery(qs_sub_cluster_code_name_en.values('name')),
                name_vi=Subquery(qs_sub_cluster_code_name_vi.values('name'))
            ).filter(id__in=categories.values_list('sub_cluster_code_id', flat=True))
            sub_cluster_code_dict = dict((o.id, o) for o in sub_cluster_codes)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="master_data_ccc_description_code.csv"'

            writer = csv.DictWriter(
                response,
                fieldnames=[
                    'Code',
                    'Name of description code (en)',
                    'Name of description code (vi)',
                    'Status',
                    'Sub cluster code',
                    'Name of sub cluster code (en)',
                    'Name of sub cluster code (vi)',
                ],
            )

            writer.writerow({
                'Code': 'Master Data/CCC Description Code',
            })

            writer.writeheader()

            for category in categories:
                sub_cluster_code = sub_cluster_code_dict.get(category.sub_cluster_code_id)
                if sub_cluster_code is None:
                    continue

                writer.writerow(
                    {
                        'Code': category.item_code,
                        'Name of description code (en)': category.name_en,
                        'Name of description code (vi)': category.name_vi,
                        'Status': "Active" if category.status else "Inactive",
                        'Sub cluster code': sub_cluster_code.item_code,
                        'Name of sub cluster code (en)': sub_cluster_code.name_en,
                        'Name of sub cluster code (vi)': sub_cluster_code.name_vi,
                    }
                )

            return response
        else:
            return Response(status=401)


def get_headers(lst):
    headers = {}
    index = 0
    for item in lst:
        headers[item.lower()] = index
        index += 1
    return headers


def get_import_column_data(headers: dict, row: List[str], name: str) -> str:
    if name not in headers.keys():
        return ""
    return row[headers[name]]


class ImportMasterDataCCCFamilyCode(APIView):
    def post(self, request, format=None):
        rows = []
        errors = {}
        headers = {}
        codes = []
        columns_used_in_import = [
            'code',
            'name of family code (en)',
            'name of family code (vi)',
            'status',
        ]
        item_updated = 0
        item_inserted = 0
        translations_updated = 0
        translations_inserted = 0
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            file = request.FILES['file']
            fs = FileSystemStorage(settings.IMPORT_DIRS)
            filename = fs.save(file.name, file)
            filepath = os.path.join(settings.IMPORT_DIRS, filename)
            import_header = 'Master Data/CCC Family Code'

            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line = 0
                for row in csv_reader:
                    if line == 0:
                        # Validate import header
                        if row[0] != import_header:
                            return Response(
                                data={
                                    'header': row[0],
                                    'exp': import_header,
                                    'code': 'import_invalid_header',
                                },
                                status=status.HTTP_200_OK)
                    elif line == 1:
                        headers = get_headers(row)
                    elif len(row) >= len(headers):
                        code = get_import_column_data(headers, row, 'code')
                        is_empty_code = code is None or len(code) == 0

                        if not is_empty_code:
                            if code not in codes:
                                codes.append(code)

                        rows.append(row)

                    line += 1
            # There are no items to be processed, abort
            if len(rows) == 0:
                return Response(
                    data={
                        'code': 'import_no_content',
                        'errors': errors,
                        'headers': headers.keys(),
                        'columns': columns_used_in_import,
                        'summary': {
                            'updated': item_updated,
                            'inserted': item_inserted,
                            'translationUpdated': translations_updated,
                            'translationInserted': translations_inserted,
                        }
                    },
                    status=status.HTTP_200_OK)
            # Retrieve main table
            items = FamilyCode.objects.filter(item_code__in=codes)
            items_dict = dict((o.item_code, o) for o in items)

            # Retrieve main table translations
            translations = FamilyCodeTranslation.objects.filter(family_code__item_code__in=codes).select_related('family_code')
            translations_dict = dict((str(o.family_code_id) + '/' + o.language_code, o) for o in translations)

            codes = []
            for row in rows:
                key = '\r\n'.join(row)
                try:
                    code = get_import_column_data(headers, row, 'code')

                    # Validate mandatory item code
                    if code is None or len(code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_item_code')
                        continue

                    # Validate duplicated item code
                    if code in codes:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('duplicated_item_code')
                        continue
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table
                try:
                    item = items_dict.get(code)
                    is_updated = item is not None
                    if not is_updated:
                        item = FamilyCode()
                        item.item_code = code

                    item_name = get_import_column_data(headers, row, 'name of family code (en)')
                    if item_name is not None and len(item_name) > 0:
                        item.name = item_name

                    item_status = get_import_column_data(headers, row, 'status')
                    if item_status is not None and len(item_status) > 0:
                        item.status = item_status == 'Active'

                    item.save()
                    codes.append(code)

                    if is_updated:
                        item_updated += 1
                    else:
                        item_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations en version
                try:
                    translation_en = get_import_column_data(headers, row, 'name of family code (en)')
                    if translation_en is not None and len(translation_en) > 0:
                        translation = translations_dict.get(str(item.id) + '/en')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = FamilyCodeTranslation()
                        translation.language_code = 'en'
                        translation.family_code_id = item.id
                        translation.name = translation_en
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations vi version
                try:

                    translation_vi = get_import_column_data(headers, row, 'name of family code (vi)')
                    if translation_vi is not None and len(translation_vi) > 0:
                        translation = translations_dict.get(str(item.id) + '/vi')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = FamilyCodeTranslation()
                        translation.language_code = 'vi'
                        translation.family_code_id = item.id
                        translation.name = translation_vi
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')

        return Response(
            data={
                'errors': errors,
                'headers': headers.keys(),
                'columns': columns_used_in_import,
                'summary': {
                    'updated': item_updated,
                    'inserted': item_inserted,
                    'translationUpdated': translations_updated,
                    'translationInserted': translations_inserted,
                }
            },
            status=status.HTTP_200_OK)


class ImportMasterDataCCCClusterCode(APIView):
    def post(self, request, format=None):
        rows = []
        errors = {}
        headers = {}
        codes = []
        fk_codes = []
        columns_used_in_import = [
            'code',
            'name of cluster code (en)',
            'name of cluster code (vi)',
            'status',
            'family code'
        ]
        item_updated = 0
        item_inserted = 0
        translations_updated = 0
        translations_inserted = 0
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            file = request.FILES['file']
            fs = FileSystemStorage(settings.IMPORT_DIRS)
            filename = fs.save(file.name, file)
            filepath = os.path.join(settings.IMPORT_DIRS, filename)
            import_header = 'Master Data/CCC Cluster Code'

            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line = 0
                for row in csv_reader:
                    if line == 0:
                        # Validate import header
                        if row[0] != import_header:
                            return Response(
                                data={
                                    'header': row[0],
                                    'exp': import_header,
                                    'code': 'import_invalid_header',
                                },
                                status=status.HTTP_200_OK)
                    elif line == 1:
                        headers = get_headers(row)
                    elif len(row) >= len(headers):
                        code = get_import_column_data(headers, row, 'code')
                        fk_code = get_import_column_data(headers, row, 'family code')
                        is_empty_code = code is None or len(code) == 0
                        is_empty_fk_code = fk_code is None or len(fk_code) == 0

                        if not is_empty_code:
                            if code not in codes:
                                codes.append(code)

                        if not is_empty_fk_code:
                            if fk_code not in fk_codes:
                                fk_codes.append(fk_code)

                        rows.append(row)

                    line += 1
            # There are no items to be processed, abort
            if len(rows) == 0:
                return Response(
                    data={
                        'code': 'import_no_content',
                        'errors': errors,
                        'headers': headers.keys(),
                        'columns': columns_used_in_import,
                        'summary': {
                            'updated': item_updated,
                            'inserted': item_inserted,
                            'translationUpdated': translations_updated,
                            'translationInserted': translations_inserted,
                        }
                    },
                    status=status.HTTP_200_OK)
            # Retrieve main table
            items = ClusterCode.objects.filter(item_code__in=codes)
            items_dict = dict((o.item_code, o) for o in items)

            # Retrieve main table translations
            translations = ClusterCodeTranslation.objects.filter(cluster_code__item_code__in=codes).select_related('cluster_code')
            translations_dict = dict((str(o.cluster_code_id) + '/' + o.language_code, o) for o in translations)

            # Retrieve foreign key
            fk_codes = FamilyCode.objects.filter(item_code__in=fk_codes)
            fk_codes_dict = dict((o.item_code, o) for o in fk_codes)

            codes = []
            for row in rows:
                key = '\r\n'.join(row)
                try:
                    code = get_import_column_data(headers, row, 'code')

                    # Validate mandatory item code
                    if code is None or len(code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_item_code')
                        continue

                    # Validate duplicated item code
                    if code in codes:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('duplicated_item_code')
                        continue

                    # Validate mandatory foreign key
                    fk_code = get_import_column_data(headers, row, 'family code')
                    if fk_code is None or len(fk_code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_fk_code')
                        continue

                    # Validate foreign key
                    fk = fk_codes_dict.get(fk_code)
                    if fk is None:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_fk_code_does_not_exist')
                        continue
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table
                try:
                    item = items_dict.get(code)
                    is_updated = item is not None
                    if not is_updated:
                        item = ClusterCode()
                        item.item_code = code
                        item.family_code_id = fk.id

                    item_name = get_import_column_data(headers, row, 'name of cluster code (en)')
                    if item_name is not None and len(item_name) > 0:
                        item.name = item_name

                    item_status = get_import_column_data(headers, row, 'status')
                    if item_status is not None and len(item_status) > 0:
                        item.status = item_status == 'Active'

                    item.save()
                    codes.append(code)

                    if is_updated:
                        item_updated += 1
                    else:
                        item_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations en version
                try:
                    translation_en = get_import_column_data(headers, row, 'name of cluster code (en)')
                    if translation_en is not None and len(translation_en) > 0:
                        translation = translations_dict.get(str(item.id) + '/en')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = ClusterCodeTranslation()
                        translation.language_code = 'en'
                        translation.cluster_code_id = item.id
                        translation.name = translation_en
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations vi version
                try:

                    translation_vi = get_import_column_data(headers, row, 'name of cluster code (vi)')
                    if translation_vi is not None and len(translation_vi) > 0:
                        translation = translations_dict.get(str(item.id) + '/vi')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = ClusterCodeTranslation()
                        translation.language_code = 'vi'
                        translation.cluster_code_id = item.id
                        translation.name = translation_vi
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')

        return Response(
            data={
                'errors': errors,
                'headers': headers.keys(),
                'columns': columns_used_in_import,
                'summary': {
                    'updated': item_updated,
                    'inserted': item_inserted,
                    'translationUpdated': translations_updated,
                    'translationInserted': translations_inserted,
                }
            },
            status=status.HTTP_200_OK)


class ImportMasterDataCCCSubClusterCode(APIView):
    def post(self, request, format=None):
        rows = []
        errors = {}
        headers = {}
        codes = []
        fk_codes = []
        columns_used_in_import = [
            'code',
            'name of sub cluster code (en)',
            'name of sub cluster code (vi)',
            'status',
            'cluster code'
        ]
        item_updated = 0
        item_inserted = 0
        translations_updated = 0
        translations_inserted = 0
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            file = request.FILES['file']
            fs = FileSystemStorage(settings.IMPORT_DIRS)
            filename = fs.save(file.name, file)
            filepath = os.path.join(settings.IMPORT_DIRS, filename)
            import_header = 'Master Data/CCC Sub Cluster Code'

            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line = 0
                for row in csv_reader:
                    if line == 0:
                        # Validate import header
                        if row[0] != import_header:
                            return Response(
                                data={
                                    'header': row[0],
                                    'exp': import_header,
                                    'code': 'import_invalid_header',
                                },
                                status=status.HTTP_200_OK)
                    elif line == 1:
                        headers = get_headers(row)
                    elif len(row) >= len(headers):
                        code = get_import_column_data(headers, row, 'code')
                        fk_code = get_import_column_data(headers, row, 'cluster code')
                        is_empty_code = code is None or len(code) == 0
                        is_empty_fk_code = fk_code is None or len(fk_code) == 0

                        if not is_empty_code:
                            if code not in codes:
                                codes.append(code)

                        if not is_empty_fk_code:
                            if fk_code not in fk_codes:
                                fk_codes.append(fk_code)

                        rows.append(row)

                    line += 1
            # There are no items to be processed, abort
            if len(rows) == 0:
                return Response(
                    data={
                        'code': 'import_no_content',
                        'errors': errors,
                        'headers': headers.keys(),
                        'columns': columns_used_in_import,
                        'summary': {
                            'updated': item_updated,
                            'inserted': item_inserted,
                            'translationUpdated': translations_updated,
                            'translationInserted': translations_inserted,
                        }
                    },
                    status=status.HTTP_200_OK)
            # Retrieve main table
            items = SubClusterCode.objects.filter(item_code__in=codes)
            items_dict = dict((o.item_code, o) for o in items)

            # Retrieve main table translations
            translations = SubClusterCodeTranslation.objects.filter(sub_cluster_code__item_code__in=codes).select_related('sub_cluster_code')
            translations_dict = dict((str(o.sub_cluster_code_id) + '/' + o.language_code, o) for o in translations)

            # Retrieve foreign key
            fk_codes = ClusterCode.objects.filter(item_code__in=fk_codes)
            fk_codes_dict = dict((o.item_code, o) for o in fk_codes)

            codes = []
            for row in rows:
                key = '\r\n'.join(row)
                try:
                    code = get_import_column_data(headers, row, 'code')

                    # Validate mandatory item code
                    if code is None or len(code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_item_code')
                        continue

                    # Validate duplicated item code
                    if code in codes:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('duplicated_item_code')
                        continue

                    # Validate mandatory foreign key
                    fk_code = get_import_column_data(headers, row, 'cluster code')
                    if fk_code is None or len(fk_code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_fk_code')
                        continue

                    # Validate foreign key
                    fk = fk_codes_dict.get(fk_code)
                    if fk is None:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_fk_code_does_not_exist')
                        continue
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table
                try:
                    item = items_dict.get(code)
                    is_updated = item is not None
                    if not is_updated:
                        item = SubClusterCode()
                        item.item_code = code
                        item.cluster_code_id = fk.id

                    item_name = get_import_column_data(headers, row, 'name of sub cluster code (en)')
                    if item_name is not None and len(item_name) > 0:
                        item.name = item_name

                    item_status = get_import_column_data(headers, row, 'status')
                    if item_status is not None and len(item_status) > 0:
                        item.status = item_status == 'Active'

                    item.save()
                    codes.append(code)

                    if is_updated:
                        item_updated += 1
                    else:
                        item_inserted += 1
                except:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations en version
                try:
                    translation_en = get_import_column_data(headers, row, 'name of sub cluster code (en)')
                    if translation_en is not None and len(translation_en) > 0:
                        translation = translations_dict.get(str(item.id) + '/en')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = SubClusterCodeTranslation()
                        translation.language_code = 'en'
                        translation.sub_cluster_code_id = item.id
                        translation.name = translation_en
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations vi version
                try:

                    translation_vi = get_import_column_data(headers, row, 'name of sub cluster code (vi)')
                    if translation_vi is not None and len(translation_vi) > 0:
                        translation = translations_dict.get(str(item.id) + '/vi')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = SubClusterCodeTranslation()
                        translation.language_code = 'vi'
                        translation.sub_cluster_code_id = item.id
                        translation.name = translation_vi
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')

        return Response(
            data={
                'errors': errors,
                'headers': headers.keys(),
                'columns': columns_used_in_import,
                'summary': {
                    'updated': item_updated,
                    'inserted': item_inserted,
                    'translationUpdated': translations_updated,
                    'translationInserted': translations_inserted,
                }
            },
            status=status.HTTP_200_OK)


class ImportMasterDataCCCCategoryCode(APIView):
    def post(self, request, format=None):
        rows = []
        errors = {}
        headers = {}
        codes = []
        fk_codes = []
        columns_used_in_import = [
            'code',
            'name of description code (en)',
            'name of description code (vi)',
            'status',
            'sub cluster code'
        ]
        item_updated = 0
        item_inserted = 0
        translations_updated = 0
        translations_inserted = 0
        if hasattr(self.request.user, 'isAdmin') and self.request.user.isAdmin():
            file = request.FILES['file']
            fs = FileSystemStorage(settings.IMPORT_DIRS)
            filename = fs.save(file.name, file)
            filepath = os.path.join(settings.IMPORT_DIRS, filename)
            import_header = 'Master Data/CCC Description Code'

            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line = 0
                for row in csv_reader:
                    if line == 0:
                        # Validate import header
                        if row[0] != import_header:
                            return Response(
                                data={
                                    'header': row[0],
                                    'exp': import_header,
                                    'code': 'import_invalid_header',
                                },
                                status=status.HTTP_200_OK)
                    elif line == 1:
                        headers = get_headers(row)
                    elif len(row) >= len(headers):
                        code = get_import_column_data(headers, row, 'code')
                        fk_code = get_import_column_data(headers, row, 'sub cluster code')
                        is_empty_code = code is None or len(code) == 0
                        is_empty_fk_code = fk_code is None or len(fk_code) == 0

                        if not is_empty_code:
                            if code not in codes:
                                codes.append(code)

                        if not is_empty_fk_code:
                            if fk_code not in fk_codes:
                                fk_codes.append(fk_code)

                        rows.append(row)

                    line += 1
            # There are no items to be processed, abort
            if len(rows) == 0:
                return Response(
                    data={
                        'code': 'import_no_content',
                        'errors': errors,
                        'headers': headers.keys(),
                        'columns': columns_used_in_import,
                        'summary': {
                            'updated': item_updated,
                            'inserted': item_inserted,
                            'translationUpdated': translations_updated,
                            'translationInserted': translations_inserted,
                        }
                    },
                    status=status.HTTP_200_OK)
            # Retrieve main table
            items = Category.objects.filter(item_code__in=codes)
            items_dict = dict((o.item_code, o) for o in items)

            # Retrieve main table translations
            translations = CategoryTranslation.objects.filter(category__item_code__in=codes).select_related('category')
            translations_dict = dict((str(o.category_id) + '/' + o.language_code, o) for o in translations)

            # Retrieve foreign key
            fk_codes = SubClusterCode.objects.filter(item_code__in=fk_codes)
            fk_codes_dict = dict((o.item_code, o) for o in fk_codes)

            codes = []
            for row in rows:
                key = '\r\n'.join(row)
                try:
                    code = get_import_column_data(headers, row, 'code')

                    # Validate mandatory item code
                    if code is None or len(code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_item_code')
                        continue

                    # Validate duplicated item code
                    if code in codes:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('duplicated_item_code')
                        continue

                    # Validate mandatory foreign key
                    fk_code = get_import_column_data(headers, row, 'sub cluster code')
                    if fk_code is None or len(fk_code) == 0:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_mandatory_fk_code')
                        continue

                    # Validate foreign key
                    fk = fk_codes_dict.get(fk_code)
                    if fk is None:
                        if key not in errors.keys():
                            errors[key] = []
                        errors[key].append('import_fk_code_does_not_exist')
                        continue
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table
                try:
                    item = items_dict.get(code)
                    is_updated = item is not None
                    if not is_updated:
                        item = Category()
                        item.item_code = code
                        item.sub_cluster_code_id = fk.id

                    item_name = get_import_column_data(headers, row, 'name of description code (en)')
                    if item_name is not None and len(item_name) > 0:
                        item.name = item_name

                    item_status = get_import_column_data(headers, row, 'status')
                    if item_status is not None and len(item_status) > 0:
                        item.status = item_status == 'Active'

                    item.save()
                    codes.append(code)

                    if is_updated:
                        item_updated += 1
                    else:
                        item_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations en version
                try:
                    translation_en = get_import_column_data(headers, row, 'name of description code (en)')
                    if translation_en is not None and len(translation_en) > 0:
                        translation = translations_dict.get(str(item.id) + '/en')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = CategoryTranslation()
                        translation.language_code = 'en'
                        translation.category_id = item.id
                        translation.name = translation_en
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')
                    continue

                # Save main table translations vi version
                try:

                    translation_vi = get_import_column_data(headers, row, 'name of description code (vi)')
                    if translation_vi is not None and len(translation_vi) > 0:
                        translation = translations_dict.get(str(item.id) + '/vi')
                        is_updated = translation is not None
                        if not is_updated:
                            translation = CategoryTranslation()
                        translation.language_code = 'vi'
                        translation.category_id = item.id
                        translation.name = translation_vi
                        translation.save()

                        if is_updated:
                            translations_updated += 1
                        else:
                            translations_inserted += 1
                except Exception as err:
                    if key not in errors.keys():
                        errors[key] = []
                    errors[key].append('import_exception')

        return Response(
            data={
                'errors': errors,
                'headers': headers.keys(),
                'columns': columns_used_in_import,
                'summary': {
                    'updated': item_updated,
                    'inserted': item_inserted,
                    'translationUpdated': translations_updated,
                    'translationInserted': translations_inserted,
                }
            },
            status=status.HTTP_200_OK)
