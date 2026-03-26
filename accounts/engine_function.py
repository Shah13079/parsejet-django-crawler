"""Scraping engines for eBay and Amazon product pages.

Contains the HTTP request logic, HTML parsing, database persistence,
and notification helpers used by the Celery tasks in accounts.task.
"""
import re
import urllib3
import requests
from os import getcwd, path
from .models import Account
from django.conf import settings
from scrapy.selector import Selector
from django.core.mail import EmailMessage
from concurrent.futures import ThreadPoolExecutor
from django.template.loader import render_to_string
from amazon_crawler.models import EbayByProduct, AmazonByProduct
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_REQUEST_RETRIES = 3

simple_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


def job_complete_mail(
    user_id, mail_subject_is, task_id, current_site, is_pages, total_products, section
):
    """Send an email notification when a scraping job finishes.

    Builds a download link for the scraped data and renders the
    job_status.html template into the email body.
    """
    if total_products != None and is_pages == None:
        pages_nd_products = "products"
        total = total_products
    elif is_pages != None and total_products is None:
        pages_nd_products = "pages"
        total = is_pages

    user = Account.objects.get(pk=user_id)
    mail_subject = mail_subject_is
    task_id = str(task_id).replace("-", "")

    if section == "AP":
        download_link = f"http://{current_site}/crawlers/download_amazon/{task_id}"
    else:
        download_link = f"http://{current_site}/crawlers/download/{task_id}"

    message = render_to_string(
        "accounts/job_status.html",
        {
            "download_link": download_link,
            "couvnt": total,
            "task_id": task_id,
            "user": user,
            "type": pages_nd_products,
        },
    )
    to_email = user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


def ebay_products_crawling(products_urls, current_user, task_id, current_site):
    """Scrape a list of eBay product URLs and persist the results.

    Iterates over each URL, extracts product fields (title, price,
    rating, brand, condition, quantities, image) via XPath selectors,
    and saves them to the database. Returns a dict with scraping stats.
    """
    logs = {}
    total_products_scraped = 0
    for each in products_urls:
        try:
            response = requests.get(each, headers=simple_headers)
            if (
                "Looks like this page is missing. If you still need help"
                in response.text
            ):
                pass
            else:
                response_selector = Selector(text=response.text)
                title = response_selector.xpath("//h1/span/text()").get()
                product_rating = response_selector.xpath(
                    '//span[@class="ux-summary__start--rating"]/span/text()'
                ).get()
                price = response_selector.xpath(
                    '//div[@class="x-price-primary"]/span/text()'
                ).get()
                price = (
                    price.strip()
                    if price
                    else response_selector.xpath(
                        '//div[@class="display-price"]/text()'
                    ).get()
                )
                brand = response_selector.xpath(
                    '//span[contains(text(),"Brand")]/ancestor::dl/dd//span/text()'
                ).get()
                condition = response_selector.xpath(
                    "//div[contains(text(),'Condition')]/following-sibling::div/text()"
                ).get()
                if condition is None:
                    condition = response_selector.xpath(
                        "//div/span[contains(text(),'Condition')]/parent::node()/following-sibling::div//span[@class='clipped']/text()"
                    ).get()
                avail_quantity = response_selector.xpath(
                    '//div[@class="d-quantity__availability"]//span[contains(text(),"available")]/text()'
                ).get()
                avail_quantity = avail_quantity.strip() if avail_quantity else None
                sold_quantity = response_selector.xpath(
                    '//div[@class="d-quantity__availability"]//span[contains(text(),"sold")]/text()'
                ).get()
                img_url = response_selector.xpath(
                    "//div/img[@fetchpriority='high']/@src"
                ).get()

                ebay_records = EbayByProduct()
                ebay_records.title = title
                ebay_records.price = price
                ebay_records.rating = product_rating
                ebay_records.brand = brand
                ebay_records.condition = condition
                ebay_records.available_quantity = avail_quantity
                ebay_records.sold_quantity = sold_quantity
                ebay_records.img_url = img_url
                ebay_records.product_url = each
                ebay_records.account = Account.objects.get(id=current_user)
                ebay_records.task_id = task_id
                ebay_records.save()
                total_products_scraped += 1

        except Exception as e:
            mail_subject = "system maintainace alert !"
            message = f"to technical team:\n\n\n\
                tool Name: [Ebay by Direct Urls]\n\n\
                file Name: engine_function.py\n\
                source link:{each}\n \
                please look into the following error in \method name[f_scrape_ebay_by_products]\n\
                \nError:\t\t{e}"

            to_email = settings.TECH_ADMIN_EMAIL
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

    logs["total_products_scraped"] = total_products_scraped
    return logs


class AmazonProduct:
    """Scraper for Amazon product pages.

    Uses Zyte proxy for requests, parses product details via XPath
    selectors, and persists results to the AmazonByProduct model.
    Supports concurrent scraping through ThreadPoolExecutor.
    """

    logs_dic = {"total_scraped_products": 0}
    headers = {
        "X-Crawlera-Region": "US",
        "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    }
    proxy_host = settings.PROXY_HOST
    proxy_port = settings.PROXY_PORT
    proxy_auth =  settings.PROXY_AUTH
    proxies = {
        "https": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
        "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
    }

    def is_amazon_choice(self, values):
        """Return True if the product has an Amazon's Choice badge, None otherwise."""
        if values and len(values) > 0:
            return True
        else:
            return None

    def remove_extra_string(self, value):
        """Strip the 'out of 5 stars' suffix from a rating string."""
        if value and "out of" in value:
            return value.replace("out of 5 stars", "")

    def get_curr(self, price):
        """Extract the currency symbol from a price string."""
        if price:
            pattern = r"(\D*)[\d\,\.]+(\D*)"
            g = re.match(pattern, price.strip()).groups()
            return (g[0] or g[1]).strip()
        else:
            return None

    def remove_curr(self, price):
        """Remove the currency symbol from a price string, returning only digits."""
        if price:
            pattern = r"(\D*)[\d\,\.]+(\D*)"
            g = re.match(pattern, price.strip()).groups()
            Currency = (g[0] or g[1]).strip()
            return price.replace(Currency, "").strip()

    def get_asin(self, href):
        """Extract the ASIN identifier from an Amazon product URL."""
        asin = re.search(r"/[dg]p/([^/?]+)", href, flags=re.IGNORECASE)
        if asin:
            return asin.group(1)

    def sending_requests(self, url, current_user, task_id, current_site, _retry_count=0):
        """Fetch an Amazon product page through the Zyte proxy.

        Retries up to MAX_REQUEST_RETRIES times on HTTP 503 responses.
        On success, delegates to parse_data for extraction.
        """
        html = requests.get(
            url,
            proxies=self.proxies,
            verify=path.join(path.join(getcwd(), "accounts"), "zyte-proxy-ca.crt"),
        )

        print("this is response from request:", html.status_code)
        if html.status_code == 503:
            if _retry_count < MAX_REQUEST_RETRIES:
                self.sending_requests(url, current_user, task_id, current_site,
                                      _retry_count=_retry_count + 1)
            else:
                print(f"Max retries ({MAX_REQUEST_RETRIES}) reached for {url}")

        elif html.status_code == 200:
            response = Selector(text=html.text)
            self.parse_data(response, current_user, task_id, current_site, str(url))

    def threading(self, urls, current_user, task_id, current_site):
        """Scrape multiple URLs concurrently using a thread pool."""
        with ThreadPoolExecutor(max_workers=15) as executor:
            for url in urls:
                executor.submit(self.sending_requests, url, current_user, task_id, url)

    def parse_data(self, response, current_user, task_id, current_site, current_url):
        """Extract product fields from an Amazon page and save to the database."""
        title = response.xpath("//h1[@id='title']/span/text()").get()
        brand = response.xpath(
            "(//td/span[contains(text(),'Brand')]/following::td)[1]/span/text()"
        ).get()
        main_price = self.remove_curr(
            response.xpath('(//span[@class="a-price-whole"])[1]/text()').get()
        )
        frac_price = self.remove_curr(
            response.xpath('//span[@class="a-price-fraction"]/text()').get()
        )

        if main_price and frac_price:
            price = main_price + "." + frac_price

        if main_price and frac_price is None:
            price = main_price

        if not main_price and not frac_price:
            price = ""

        ratings = self.remove_extra_string(
            response.xpath(
                '(//span[contains(text(),"out of 5 stars")])[1]/text()'
            ).get()
        )
        asin = self.get_asin(current_url)
        amazon_choice = response.xpath("//span[contains(text(),'Choice')]/text()").get()
        if amazon_choice is not None:
            amazon_choice = True
        else:
            amazon_choice = None
        try:
            amazon_records = AmazonByProduct()
            amazon_records.title = title
            amazon_records.price = price
            amazon_records.brand = brand
            amazon_records.rating = ratings
            amazon_records.asin = asin
            amazon_records.product_url = current_url
            amazon_records.amazon_choice = amazon_choice
            amazon_records.task_id = task_id
            amazon_records.account = Account.objects.get(id=current_user)
            amazon_records.save()
            self.logs_dic["total_scraped_products"] += 1

        except Exception as e:
            mail_subject = "System maintainace alert !"
            message = f"To Technical team:\n\n\n\
                Tool Name: [Amazon Data]\n\n\
                file Name: engine_function.py\n\
                source link:{current_url}\n \
                Please Look at the following error in \nmethod name[amazon: parse_data]\n\
                \nError:\t\t{e}"

            to_email = settings.TECH_ADMIN_EMAIL
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

    def logs_mail(self, current_user, task_id, current_site):
        """Send a job completion email if at least one product was scraped."""
        if self.logs_dic["total_scraped_products"] >= 1:
            subject = f"amazon by products job status - ParseJet"
            job_complete_mail(
                current_user,
                subject,
                task_id,
                current_site,
                None,
                self.logs_dic["total_scraped_products"],
                "AP",  # This just a sign symbols to differ products/categories
            )


def amazon_product_calling(products_urls, current_user, task_id, current_site):
    """Entry point for the Amazon scraping pipeline.

    Creates an AmazonProduct instance, runs concurrent scraping across
    all provided URLs, and sends a summary notification email.
    """
    print("Product url received in amazon class object:", products_urls)
    object1 = AmazonProduct()
    object1.threading(products_urls, current_user, task_id, current_site)
    object1.logs_mail(current_user, task_id, current_site)
