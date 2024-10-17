"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from graphene_file_upload.django import FileUploadGraphQLView

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response(
        {
            'auth': {
                'login': reverse('auth-login', request=request, format=format),
                'logout': reverse('auth-logout', request=request, format=format),
                'forgot-password': reverse('auth-forgot-password', request=request, format=format),
                'check-forgot-password-token': reverse('auth-check-forgot-password-token', request=request, format=format),
                'create-new-password': reverse('auth-create-new-password', request=request, format=format),
                'create-supplier': reverse('auth-create-supplier', request=request, format=format),
                'create-buyer': reverse('auth-create-buyer', request=request, format=format),
                'activate-account': reverse('auth-activate-account', request=request, format=format),
            },
            'auctions': {
                'list': reverse('auction-list', request=request, format=format),
                'create': reverse('auction-create', request=request, format=format),
            },
            'users': {
                'profile': reverse('user-profile', request=request, format=format),
                'suppliers': reverse('user-supplier-list', request=request, format=format),
                'buyers': reverse('user-buyer-list', request=request, format=format),
            },
            'master-data': {
                'country': reverse('master-data-country-list', request=request, format=format),
                'country-state': reverse('master-data-country-state-list', request=request, format=format),
                'currency': reverse('master-data-currency-list', request=request, format=format),
                'family-code': reverse('master-data-family-code-list', request=request, format=format),
                'cluster-code': reverse('master-data-cluster-code-list', request=request, format=format),
                'sub-cluster-code': reverse('master-data-sub-cluster-code-list', request=request, format=format),
                'category': reverse('master-data-category-list', request=request, format=format),
                'contract-type': reverse('master-data-contract-type-list', request=request, format=format),
                'payment-term': reverse('master-data-payment-term-list', request=request, format=format),
                'delivery-term': reverse('master-data-delivery-term-list', request=request, format=format),
                'unit-of-measure': reverse('master-data-unit-of-measure-list', request=request, format=format),
                'email-templates': reverse('master-data-email-templates-list', request=request, format=format),
                'number-of-employee': reverse('master-data-number-of-employee-list', request=request, format=format),
                'gender': reverse('master-data-gender-list', request=request, format=format),
                'technical-weighting': reverse('master-data-technical-weighting-list', request=request, format=format),
                'auction-type': reverse('master-data-auction-type-list', request=request, format=format),
                'position': reverse('master-data-position-list', request=request, format=format),
                'level': reverse('master-data-level-list', request=request, format=format),
            },
        }
    )


urlpatterns = [
    path('api/', api_root),
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.auctions.urls')),
    path('api/master-data/', include('apps.master_data.urls')),
    path('api/admin/', admin.site.urls),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT})
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)  
      