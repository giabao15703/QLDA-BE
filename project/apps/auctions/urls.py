from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from apps.auctions import views
from apps.users.schema import import_students


urlpatterns = format_suffix_patterns(
    [
        path('auction/', views.AuctionList.as_view(), name='auction-list'),
        path('auction/create/', views.CreateAuction.as_view(), name='auction-create'),
        path('auction/<int:pk>/', views.AuctionDetail.as_view(), name='auction-detail'),
        path('auction/<int:pk>/options/', views.AuctionOptions.as_view(), name='auction-options'),
        path('auction/<int:pk>/results/', views.AuctionResultsList.as_view(), name='auction-results'),
        path('auction/<int:pk>/confirm/', views.AuctionConfirm.as_view(), name='auction-confirm'),
        path('server/', views.CurrentTimestamp.as_view(), name='auction-server-time'),
        path('auction/extract/coupon/', views.AuctionReportExportCoupon.as_view(), name='auction-extract-coupon'),
        path('import-students/', import_students, name='import-students'),

    ]
)

