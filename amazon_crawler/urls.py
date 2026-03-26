"""URL configuration for the amazon_crawler app."""
from django.urls import path
from . import views

app_name = 'amazon_crawler'

urlpatterns = [
    path('', views.home, name=''),
    path('best-selling/', views.home, name='best-selling'),
    path('download/<task_id>/', views.download_data, name='download_data'),
    path('download_amazon/<task_id>/', views.download_amazon, name='download_amazon'),
    path('EBP/', views.ebay_by_products, name='EBP'),
    path('ABP/', views.amazon_by_pro, name='ABP'),
]
