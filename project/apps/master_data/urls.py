from apps.master_data import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    #1st-------------------------------------------------------
    path('country/', views.CountryList.as_view(), name='master-data-country-list'),
    path('country/<int:pk>/', views.CountryDetail.as_view(), name='master-data-country-detail'),
    #2nd--------------------------------------------------------
    path('currency/', views.CurrencyList.as_view(), name='master-data-currency-list'),
    path('currency/<int:pk>/', views.CurrencyDetail.as_view(), name='master-data-currency-detail'),
    #3rd--------------------------------------------------------
    path('family-code/', views.FamilyCodeList.as_view(), name='master-data-family-code-list'),
    path('family-code/<int:pk>/', views.FamilyCodeDetail.as_view(), name='master-data-family-code-detail'),
    #4th-----------------------------------------------------
    path('cluster-code/', views.ClusterCodeList.as_view(), name='master-data-cluster-code-list'),
    path('cluster-code/<int:pk>/', views.ClusterCodeDetail.as_view(), name='master-data-cluster-code-detail'),
    #5th-----------------------------------------------------
    path('sub-cluster-code/', views.SubClusterCodeList.as_view(), name='master-data-sub-cluster-code-list'),
    path('sub-cluster-code/<int:pk>/', views.SubClusterCodeDetail.as_view(), name='master-data-sub-cluster-code-detail'),
    #6th-----------------------------------------------------
    path('category/', views.CategoryList.as_view(), name='master-data-category-list'),
    path('category/<int:pk>/', views.CategoryDetail.as_view(), name='master-data-category-detail'),
    #7th-----------------------------------------------------
    path('contract-type/', views.ContractTypeList.as_view(), name='master-data-contract-type-list'),
    path('contract-type/<int:pk>/', views.ContractTypeDetail.as_view(), name='master-data-contract-type-detail'),
    #8th-----------------------------------------------------
    path('payment-term/', views.PaymentTermList.as_view(), name='master-data-payment-term-list'),
    path('payment-term/<int:pk>/', views.PaymentTermDetail.as_view(), name='master-data-payment-term-detail'),
    #9th-----------------------------------------------------
    path('delivery-term/', views.DeliveryTermList.as_view(), name='master-data-delivery-term-list'),
    path('delivery-term/<int:pk>/', views.DeliveryTermDetail.as_view(), name='master-data-delivery-term-detail'),
    #10th-----------------------------------------------------
    path('unit-of-measure/', views.UnitofMeasureList.as_view(), name='master-data-unit-of-measure-list'),
    path('unit-of-measure/<int:pk>/', views.UnitofMeasureDetail.as_view(), name='master-data-unit-of-measure-detail'),
    #11th-----------------------------------------------------
    path('email-templates/', views.EmailTemplatesList.as_view(), name='master-data-email-templates-list'),
    path('email-templates/<int:pk>/', views.EmailTemplatesDetail.as_view(), name='master-data-email-templates-detail'),
    #12th----------------------------------------------------
    path('number-of-employee/', views.NumberofEmployeeList.as_view(), name='master-data-number-of-employee-list'),
    path('number-of-employee/<int:pk>/', views.NumberofEmployeeDetail.as_view(), name='master-data-number-of-employee-detail'),
    #13th----------------------------------------------------
    path('gender/', views.GenderList.as_view(), name='master-data-gender-list'),
    path('gender/<int:pk>/', views.GenderDetail.as_view(), name='master-data-gender-detail'),
    #14th----------------------------------------------------
    path('technical-weighting/', views.TechnicalWeightingList.as_view(), name='master-data-technical-weighting-list'),
    path('auction-type/', views.AuctionTypeList.as_view(), name='master-data-auction-type-list'),
    #15th--------------------------------------------------------
    path('level/', views.LevelView.as_view(), name='master-data-level-list'),
    path('level/<int:pk>/', views.LevelDetailView.as_view(), name='master-data-level-detail'),
    #16th--------------------------------------------------------#
    path('position/', views.PositionView.as_view(), name='master-data-position-list'),
    path('position/<int:pk>/', views.PositionDetailView.as_view(), name='master-data-position-detail'),
    #17th-------------------------------------------------------
    path('country-state/', views.CountryStateList.as_view(), name='master-data-country-state-list'),
    path('country-state/<int:pk>/', views.CountryStateDetail.as_view(), name='master-data-country-state-detail'),

    # Export
    path('export/ccc-family-code', views.ExportMasterDataCCCFamilyCode.as_view(), name='master-data-export-ccc-family-code'),
    path('export/ccc-cluster-code', views.ExportMasterDataCCCClusterCode.as_view(), name='master-data-export-ccc-cluster-code'),
    path('export/ccc-sub-cluster-code', views.ExportMasterDataCCCSubClusterCode.as_view(), name='master-data-export-ccc-sub-cluster-code'),
    path('export/ccc-description-code', views.ExportMasterDataCCCCategory.as_view(), name='master-data-export-ccc-description-code'),

    # Import
    path('import/ccc-family-code', views.ImportMasterDataCCCFamilyCode.as_view(), name='master-data-import-ccc-family-code'),
    path('import/ccc-cluster-code', views.ImportMasterDataCCCClusterCode.as_view(), name='master-data-import-ccc-cluster-code'),
    path('import/ccc-sub-cluster-code', views.ImportMasterDataCCCSubClusterCode.as_view(), name='master-data-import-ccc-sub-cluster-code'),
    path('import/ccc-description-code', views.ImportMasterDataCCCCategoryCode.as_view(), name='master-data-import-ccc-description-code'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
