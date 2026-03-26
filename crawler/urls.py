"""Root URL configuration for the crawler project."""
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from amazon_crawler import views
from django.conf.urls.static import static

admin.site.site_header = 'ParseJet'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crawlers/', include('amazon_crawler.urls')),
    path('', views.home),
    path('accounts/', include('accounts.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
