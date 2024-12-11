# apps/users/urls.py
from django.urls import path
from apps.users.views import (
    SupplierList,
    BuyerList,
    ProfileView,
    ChangePasswordView,
    AdminPermissionExport,
    BuyerExport,
    SupplierExport,
    DownloadSupplierForm,
    PromotionExport,
    PromotionUserUsedExport,
    DownloadSupplierCooperationAgreement,
)
from apps.users.views import export_students, export_de_tai
urlpatterns = [
    path('user/profile/', ProfileView.as_view(), name='user-profile'),
    path('user/change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('supplier/', SupplierList.as_view(), name='user-supplier-list'),
    path('supplier/download-cooperation-agreement/', DownloadSupplierCooperationAgreement.as_view(), name='download-cooperation-agreement'),
    path('buyer/', BuyerList.as_view(), name='user-buyer-list'),
    path('admin/export/', AdminPermissionExport.as_view(), name='user-admin-permission_export'),
    path('buyer/export/', BuyerExport.as_view(), name='user-buyer-export'),
    path('export/', export_students, name='export_students'),
    path('export-de-tai/', export_de_tai, name='export_de_tai'),
    path('supplier/export/', SupplierExport.as_view(), name='user-supplier-export'),
    path('supplier/download-form/', DownloadSupplierForm.as_view(), name='supplier-download-form'),
    path('promotion/export/', PromotionExport.as_view(), name='promotion-export'),
    path('promotion_history/export/', PromotionUserUsedExport.as_view(), name='promotion-history-export'),
]
