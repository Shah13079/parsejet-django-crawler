"""Database models for scraped eBay and Amazon product data."""
from django.db import models
from accounts.models import Account


class EbayByProduct(models.Model):
    """Stores scraped product data from a single eBay listing."""

    title = models.CharField(max_length=300, null=True)
    price = models.CharField(max_length=20, null=True)
    rating = models.CharField(max_length=20, null=True)
    condition = models.CharField(max_length=250, null=True)
    brand = models.CharField(max_length=250, null=True)
    available_quantity = models.CharField(max_length=250, null=True)
    sold_quantity = models.CharField(max_length=250, null=True)
    img_url = models.CharField(max_length=250, null=True)
    product_url = models.CharField(max_length=250, null=True)
    task_id = models.UUIDField(null=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='user_account', null=False
    )

    def __str__(self) -> str:
        return self.title or ''

    class Meta:
        ordering = ['title', 'price']


class AmazonByProduct(models.Model):
    """Stores scraped product data from a single Amazon listing."""

    title = models.CharField(max_length=300, null=True)
    price = models.CharField(max_length=20, null=True)
    rating = models.CharField(max_length=250, null=True)
    brand = models.CharField(max_length=250, null=True)
    asin = models.CharField(max_length=250, null=True)
    amazon_choice = models.CharField(max_length=250, null=True)
    product_url = models.CharField(max_length=700, null=True)
    task_id = models.UUIDField(null=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='user_account_id', null=False
    )

    def __str__(self) -> str:
        return self.title or ''

    class Meta:
        ordering = ['title', 'price']
