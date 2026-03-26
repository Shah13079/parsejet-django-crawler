# ParseJet

A web application for scraping product data from Amazon and eBay. ParseJet provides a browser-based interface so users can submit product URLs, run background scraping jobs, and download the results as CSV files -- no scripts, libraries, or command-line knowledge required.

Live site: [parsejet.com](http://www.parsejet.com)

---

## Features

- Scrape eBay product listings by direct URL (title, price, rating, brand, condition, quantity, image)
- Scrape Amazon product listings by direct URL (title, price, rating, brand, ASIN, Amazon's Choice badge)
- Background job processing via Celery and Redis
- Email notifications with CSV download links on job completion
- User authentication with email verification and password reset
- CSV export for all scraped data
- Admin panel for managing scraped records

---

## Tech Stack

- **Backend:** Python 3.11+, Django 4.2
- **Task Queue:** Celery 5.4, Redis
- **Scraping:** Requests, Scrapy Selectors
- **Database:** SQLite (development), PostgreSQL-ready (production)
- **Frontend:** Django Templates, Bootstrap
- **Deployment:** Gunicorn, WhiteNoise (static files), Heroku-compatible

---

## Architecture

```
Browser (User)
    |
    v
Django Views  --->  Celery Task Queue  --->  Redis Broker
    |                     |
    |                     v
    |              Scraping Engine
    |              (Requests + Scrapy Selectors)
    |                     |
    |                     v
    |               Parse HTML
    |               Extract fields
    |                     |
    v                     v
 SQLite/PostgreSQL  <--- Save records
    |                     |
    v                     v
 CSV Export         Email notification
 (download link)    (with download link)
```

---

## Screenshots

The live application is available at [parsejet.com](http://www.parsejet.com).

---

## Installation and Setup

### Prerequisites

- Python 3.11+
- Redis server running locally (default: `localhost:6379`)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/parsejet-django-crawler.git
   cd parsejet-django-crawler
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the required environment variables (see below).

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

7. In a separate terminal, start the Celery worker:
   ```bash
   celery -A crawler.cele worker --pool=solo -l info
   ```

---

## Usage

1. Register an account and verify your email.
2. Log in and select a scraping tool (Amazon or eBay).
3. Paste one or more product URLs (one per line).
4. Submit the job. You will receive an email when scraping is complete.
5. Use the download link in the email to get your CSV file.

---

## Project Structure

```
parsejet-django-crawler/
|-- accounts/                # User auth app (models, views, forms, Celery tasks)
|   |-- engine_function.py   # Scraping engines for eBay and Amazon
|   |-- forms.py             # Registration and profile forms
|   |-- models.py            # Custom Account user model
|   |-- task.py              # Celery task definitions
|   |-- urls.py              # Auth-related URL routes
|   +-- views.py             # Auth views (register, login, password reset)
|
|-- amazon_crawler/          # Scraping app (models, views, admin, templates)
|   |-- admin.py             # Admin registration for scraped data models
|   |-- models.py            # EbayByProduct, AmazonByProduct models
|   |-- urls.py              # Crawler URL routes
|   |-- views.py             # Scraping submission and CSV download views
|   +-- templates/           # HTML templates (base, forms, emails)
|
|-- crawler/                 # Django project configuration
|   |-- cele.py              # Celery app setup
|   |-- settings.py          # Django settings
|   |-- urls.py              # Root URL configuration
|   +-- wsgi.py              # WSGI entry point
|
|-- manage.py
|-- requirements.txt
+-- Procfile                 # Heroku process definitions
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=
DEBUG=
TECH_ADMIN_EMAIL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
PROXY_HOST=
PROXY_PORT=
PROXY_AUTH=
```

| Variable             | Description                                      |
|----------------------|--------------------------------------------------|
| `SECRET_KEY`         | Django secret key                                |
| `DEBUG`              | Enable debug mode (`True` or `False`)            |
| `TECH_ADMIN_EMAIL`   | Email for system error alerts                    |
| `EMAIL_HOST_USER`    | Gmail address for sending transactional emails   |
| `EMAIL_HOST_PASSWORD`| Gmail app password                               |
| `PROXY_HOST`         | Zyte proxy hostname                              |
| `PROXY_PORT`         | Zyte proxy port                                  |
| `PROXY_AUTH`         | Zyte proxy authentication key                    |

---

## Author

Shah Hussain -- [parsejet.com](http://www.parsejet.com)

---

## License

This project is licensed under the MIT License.
