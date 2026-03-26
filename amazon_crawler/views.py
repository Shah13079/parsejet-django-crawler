"""Views for the crawler tools: eBay/Amazon scraping and CSV downloads."""
import csv
import uuid
from django.db.models import Q
from django.contrib import auth
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from amazon_crawler.models import EbayByProduct, AmazonByProduct
from accounts.task import scrape_ebay_by_products, scrape_amazon_products


def home(request):
    """Render the landing page."""
    return render(request, 'crawl.html')


@login_required
def ebay_by_products(request):
    """Accept eBay product URLs from the user and dispatch a Celery scraping task.

    Validates that the submitted URLs belong to eBay and are not
    paginated search results before queuing the background job.
    """
    current_user = auth.get_user(request)
    current_user_id = current_user.id
    current_site = get_current_site(request)

    if request.method == 'POST':
        products_urls = request.POST.get('EBP')
        task_id = uuid.uuid4()
        if 'ebay' not in products_urls or 'pgn=' in products_urls:
            messages.warning(request, 'Please paste valid URLs of eBay products!')
            return render(request, 'ebay_by_products.html', {'url_error': True})

        elif 'ebay' in products_urls:
            products_urls = products_urls.split()
            scrape_ebay_by_products.delay(
                products_urls, current_user_id, task_id, str(current_site)
            )
            messages.success(
                request,
                f'Your task: [{task_id}] has been added successfully. '
                f'You will be notified via email when the job finishes!'
            )
            return render(request, 'ebay_by_products.html', {'entities': 'entities'})
    return render(request, 'ebay_by_products.html')


@login_required
def amazon_by_pro(request):
    """Accept Amazon product URLs from the user and dispatch a Celery scraping task.

    Validates that the submitted URLs belong to Amazon before queuing
    the background job.
    """
    current_user = auth.get_user(request)
    current_user_id = current_user.id
    current_site = get_current_site(request)

    if request.method == 'POST':
        products_urls = request.POST.get('ABP')
        task_id = uuid.uuid4()

        if 'amazon' not in products_urls:
            messages.warning(request, 'Please paste valid URLs of Amazon products!')
            return render(request, 'amazon_by_products.html', {'url_error': True})

        if 'amazon' in products_urls:
            products_urls = products_urls.split()
            messages.success(
                request,
                f'Your task: [{task_id}] has been added successfully. '
                f'You will be notified via email when the job finishes!'
            )
            scrape_amazon_products.delay(
                products_urls, current_user_id, task_id, str(current_site)
            )
            return redirect('Amazon_crawler:amazon-products')
    return render(request, 'amazon_by_products.html', {'url_error': True})


@login_required
def download_data(request, task_id):
    """Export scraped eBay product data as a downloadable CSV file.

    Filters results by the authenticated user and the given task ID.
    """
    if request.user.is_authenticated:
        current_user = auth.get_user(request)
        current_user_id = current_user.id
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow([
            'title', 'price', 'rating', 'shipping', 'condition',
            'brand', 'available_quantity', 'sold_quantity', 'img_url', 'product_url'
        ])
        query_set = EbayByProduct.objects.filter(
            Q(account_id=int(current_user_id)) & Q(task_id=task_id)
        ).values_list(
            'title', 'price', 'rating', 'condition', 'brand',
            'available_quantity', 'sold_quantity', 'img_url', 'product_url',
        )

        for each in query_set:
            writer.writerow(each)
        response['Content-Disposition'] = 'attachment; filename="Ebay-scraped.csv"'
        return response
    else:
        return redirect('login')


@login_required
def download_amazon(request, task_id):
    """Export scraped Amazon product data as a downloadable CSV file.

    Filters results by the authenticated user and the given task ID.
    """
    if request.user.is_authenticated:
        current_user = auth.get_user(request)
        current_user_id = current_user.id

        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['title', 'price', 'rating', 'brand', 'asin', 'amazon_choice', 'product_url'])
        # Filter by user account and the task UUID
        query_set = AmazonByProduct.objects.filter(
            Q(account_id=int(current_user_id)) & Q(task_id=task_id)
        ).values_list(
            'title', 'price', 'rating', 'brand', 'asin', 'amazon_choice', 'product_url'
        )

        for each in query_set:
            writer.writerow(each)
        response['Content-Disposition'] = 'attachment; filename="amazon-data-scraped.csv"'
        return response
    else:
        return redirect('login')
