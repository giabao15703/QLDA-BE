from apps.authentication import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns([
    path('authentication/login/', views.Login.as_view(), name='auth-login'),
    path('authentication/logout/', views.Logout.as_view(), name='auth-logout'),
    path('authentication/forgot-password/', views.ForgotPassword.as_view(), name='auth-forgot-password'),
    path('authentication/check-forgot-password-token/', views.CheckForgotPasswordToken.as_view(), name='auth-check-forgot-password-token'),
    path('authentication/create-new-password/', views.CreateNewPassword.as_view(), name='auth-create-new-password'),
    path('authentication/create-supplier/', views.CreateSupplier.as_view(), name='auth-create-supplier'),
    path('authentication/create-buyer/', views.CreateBuyer.as_view(), name='auth-create-buyer'),
    path('authentication/activate-account/', views.ActivateAccount.as_view(), name='auth-activate-account'),
])
