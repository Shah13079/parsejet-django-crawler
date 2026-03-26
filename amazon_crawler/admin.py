"""Admin configuration for the amazon_crawler app."""
from django.contrib import admin
from amazon_crawler import models


class EbayProductAdmin(admin.ModelAdmin):
    """Admin view for scraped eBay product records."""

    list_display = ['title', 'price', 'rating', 'brand', 'condition', 'product_url']
    ordering = ['title', 'price']
    list_per_page = 50


admin.site.register(models.EbayByProduct, EbayProductAdmin)


class AmazonProductAdmin(admin.ModelAdmin):
    """Admin view for scraped Amazon product records."""

    list_display = ['title', 'price', 'rating', 'brand', 'asin', 'product_url']
    ordering = ['title', 'price']
    list_per_page = 50


admin.site.register(models.AmazonByProduct, AmazonProductAdmin)
