from django.contrib import admin
from amazon_crawler import models

# Register your models here.
class EbayProductAdmin(admin.ModelAdmin):
    list_display=['title','price','rating','brand','condition','product_url']
    ordering=['title','price']
    list_per_page=50
admin.site.register(models.EbayByProduct,EbayProductAdmin)

class AmazonProductAdmin(admin.ModelAdmin):
    list_display=['title','price','rating','brand','asin','product_url']
    ordering=['title','price']
    list_per_page=50
admin.site.register(models.AmazonByProduct,AmazonProductAdmin)
