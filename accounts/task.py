from celery import shared_task
from .engine_function import *
from accounts.models import Account
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

@shared_task(bind=True)
def scrape_amazon_products(self, products_urls, current_user, task_id, current_site):
    """Celery task that scrapes product data from a list of Amazon URLs.

    Delegates to amazon_product_calling which handles concurrent
    fetching, parsing, database persistence, and email notification.
    """
    amazon_product_calling(products_urls, current_user, task_id, current_site)

@shared_task(bind=True)
def sending_activation_mail(self, template_name, current_site, user_id, email, sub):
    """Celery task that sends an account activation or password-reset email.

    Renders the specified template with a unique token link and
    delivers it as an HTML email to the user.
    """
    user = Account.objects.get(pk=user_id)
    message = render_to_string(
        f"accounts/{template_name}.html",
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )

    to_email = user.email
    mail_subject = sub
    text_content = ""
    html_content = message
    msg = EmailMultiAlternatives(mail_subject, text_content, email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task(bind=True)
def scrape_ebay_by_products(self, products_urls, current_user, task_id, current_site):
    """Celery task that scrapes product data from a list of eBay URLs.

    Calls the eBay crawling engine, then sends a job-complete
    notification email if at least one product was scraped.
    """
    print("These are all my products:", products_urls)

    logs = ebay_products_crawling(products_urls, current_user, task_id, current_site)
    if isinstance(logs, dict):
        total_prosucts = logs["total_products_scraped"]
        if int(total_prosucts) >= 1:
            subject = f"Parsejet Ebay by products job status "
            job_complete_mail(
                current_user, subject, task_id, current_site, None, total_prosucts, ""
            )
