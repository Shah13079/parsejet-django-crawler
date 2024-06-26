# Generated by Django 4.2 on 2024-04-22 20:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EbayByProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=300, null=True)),
                ("price", models.CharField(max_length=20, null=True)),
                ("rating", models.CharField(max_length=20, null=True)),
                ("condition", models.CharField(max_length=250, null=True)),
                ("brand", models.CharField(max_length=250, null=True)),
                ("available_quantity", models.CharField(max_length=250, null=True)),
                ("sold_quantity", models.CharField(max_length=250, null=True)),
                ("img_url", models.CharField(max_length=250, null=True)),
                ("product_url", models.CharField(max_length=250, null=True)),
                ("task_id", models.UUIDField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_account",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["title", "price"],
            },
        ),
        migrations.CreateModel(
            name="AmazonByProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=300, null=True)),
                ("price", models.CharField(max_length=20, null=True)),
                ("rating", models.CharField(max_length=250, null=True)),
                ("brand", models.CharField(max_length=250, null=True)),
                ("asin", models.CharField(max_length=250, null=True)),
                ("amazon_choice", models.CharField(max_length=250, null=True)),
                ("product_url", models.CharField(max_length=700, null=True)),
                ("task_id", models.UUIDField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_account_id",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["title", "price"],
            },
        ),
    ]
