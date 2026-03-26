"""URL configuration for the accounts app."""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.view_login, name='login'),
    path('logout/', views.logouting, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotpassword', views.forgot_password, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
]

