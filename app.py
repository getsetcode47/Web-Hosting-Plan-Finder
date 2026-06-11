import csv
import os
import re
from io import StringIO
from datetime import datetime
from functools import wraps

from flask import Flask, abort, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_sitemap import Sitemap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash


def env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


IS_PRODUCTION = env_flag('FLASK_ENV') or env_flag('APP_ENV') or env_flag('PRODUCTION')
SITE_URL = os.environ.get('SITE_URL', '').rstrip('/')

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = env_flag('SESSION_COOKIE_SECURE', IS_PRODUCTION)
app.config['REMEMBER_COOKIE_SECURE'] = env_flag('REMEMBER_COOKIE_SECURE', IS_PRODUCTION)
app.config['PREFERRED_URL_SCHEME'] = 'https' if IS_PRODUCTION else 'http'

if IS_PRODUCTION and app.config['SECRET_KEY'] == 'dev-secret-change-me':
    raise RuntimeError('SECRET_KEY must be set in production.')

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

sitemap = Sitemap(app=app)
db = SQLAlchemy(app)

PROVIDER_LOGOS = {
    'hostinger': '/static/provider-logos/hostinger.svg',
    'bluehost': '/static/provider-logos/bluehost.svg',
    'godaddy': '/static/provider-logos/godaddy.svg',
    'bigrock': '/static/provider-logos/bigrock.svg',
    'namecheap': '/static/provider-logos/namecheap.svg',
    'siteground': '/static/provider-logos/siteground.svg',
    'a2hosting': '/static/provider-logos/a2hosting.svg',
    'digitalocean': '/static/provider-logos/digitalocean.svg',
    'vultr': '/static/provider-logos/vultr.svg',
    'amazon web services': '/static/provider-logos/aws.svg',
    'aws': '/static/provider-logos/aws.svg',
    'linode': '/static/provider-logos/linode.svg',
    'akamai': '/static/provider-logos/akamai.svg',
}

HOSTING_TYPE_CHOICES = [
    ('shared', 'Shared Hosting'),
    ('vps', 'VPS Hosting'),
    ('cloud', 'Cloud Hosting'),
    ('dedicated', 'Dedicated Server'),
]

HOSTING_TYPE_LABELS = dict(HOSTING_TYPE_CHOICES)

PLAN_BUDGET_RULES = {
    'shared': {'min_budget': 50, 'budget_multiplier': 3.0},
    'vps': {'min_budget': 500, 'budget_multiplier': 3.0},
    'cloud': {'min_budget': 200, 'budget_multiplier': 3.0},
    'dedicated': {'min_budget': 7000, 'budget_multiplier': 3.0},
}

SEO_PAGE_DEFAULTS = {
    'home': {
        'title': 'CB4UHost - Hosting Comparison Platform & IT Services',
        'description': 'Compare hosting providers, review pricing, and discover IT services from CB4UHost and W-Tech.',
    },
    'calculator': {
        'title': 'Hosting Plan Calculator & Comparison Tool | CB4UHost',
        'description': 'Compare hosting plans by price, storage, websites, SSL, migration, and performance to find the right hosting provider faster.',
    },
    'hosting_comparison_2026': {
        'title': 'Web Hosting Comparison Tool 2026 | CB4UHost',
        'description': 'Compare Hostinger, Bluehost, SiteGround, and CB4UHost instantly. Use our tool to find the cheapest NVMe hosting with free migration and SSL. Save up to 70% today.',
    },
    'about': {
        'title': 'About CB4UHost & W-Tech',
        'description': 'Learn about CB4UHost, our hosting comparison platform, and W-Tech’s digital infrastructure, migration, security, and managed services.',
    },
    'contact': {
        'title': 'Contact CB4UHost & W-Tech',
        'description': 'Contact CB4UHost for hosting help, migration planning, managed services, security consulting, and infrastructure strategy.',
    },
    'service1': {
        'title': 'Cloud & Infrastructure Strategy | W-Tech',
        'description': 'Plan cloud and infrastructure strategy with W-Tech. Compare options, reduce cost, and improve performance before you migrate or scale.',
    },
    'service2': {
        'title': 'Migration Services | W-Tech',
        'description': 'Website, hosting, and infrastructure migration services from W-Tech with planning, execution, and transition support.',
    },
    'service3': {
        'title': 'Managed Services | W-Tech',
        'description': 'Managed services for uptime, monitoring, optimization, and operational support across hosting and cloud environments.',
    },
    'service4': {
        'title': 'Digital Security & Compliance | W-Tech',
        'description': 'Security and compliance services for hosting, cloud, and digital infrastructure with practical risk reduction and audit readiness.',
    },
    'service5': {
        'title': 'Digital Transformation & Future-Proofing | W-Tech',
        'description': 'Digital transformation services that help teams modernize infrastructure, improve agility, and future-proof critical systems.',
    },
    'blog_list': {
        'title': 'Hosting, Cloud & Infrastructure Blog | CB4UHost',
        'description': 'Read hosting, cloud, security, migration, and infrastructure insights from the CB4UHost and W-Tech blog.',
    },
    'privacy_policy': {
        'title': 'Privacy Policy | CB4UHost',
        'description': 'Read the privacy policy for CB4UHost and W-Tech.',
    },
    'terms_of_service': {
        'title': 'Terms of Service | CB4UHost',
        'description': 'Review the terms of service for the CB4UHost website and services.',
    },
    'cookie_policy': {
        'title': 'Cookie Policy | CB4UHost',
        'description': 'Learn how cookies and similar technologies are used across the CB4UHost website.',
    },
}


def absolute_url(path=''):
    if SITE_URL:
        return f"{SITE_URL}{path}"
    if not request:
        return path
    return f"{request.url_root.rstrip('/')}{path}"


def build_seo_meta(endpoint=None, **overrides):
    endpoint = endpoint or request.endpoint or ''
    defaults = {
        'title': 'CB4UHost - Hosting Comparison Platform',
        'description': 'Compare hosting providers, pricing, performance, and services with CB4UHost.',
        'robots': 'index,follow',
        'og_type': 'website',
        'site_name': 'CB4UHost',
        'canonical': request.base_url,
    }
    defaults.update(SEO_PAGE_DEFAULTS.get(endpoint, {}))
    defaults.update(overrides)
    return defaults


@app.context_processor
def inject_provider_assets():
    return {
        'provider_logos': PROVIDER_LOGOS,
        'seo_meta': build_seo_meta(),
    }


@app.after_request
def set_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    return response

@sitemap.register_generator
def sitemap_pages():
    yield 'home', {}
    yield 'calculator', {}
    yield 'hosting_comparison_2026', {}
    yield 'about', {}
    yield 'blog_list', {}
    yield 'contact', {}
    yield 'service1', {}
    yield 'service2', {}
    yield 'service3', {}
    yield 'service4', {}
    yield 'service5', {}
    yield 'privacy_policy', {}
    yield 'terms_of_service', {}
    yield 'cookie_policy', {}

# Hosting plans data (Shared Hosting)
# Hosting plans data
hosting_data = {
    "hostinger": {
        "Single": {
            "price": 69,
            "regular_price": 399,
            "websites": 1,
            "storage": "10 GB",
            "storage_value": 10,
            "type": "SSD",
            "bandwidth": "100 GB",
            "bandwidth_value": 100,
            "email": "1 Email",
            "free_domain": False,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Weekly Backups",
            "popular": False,
            "best_for": "Beginners"
        },
        "Premium": {
            "price": 149,
            "regular_price": 599,
            "websites": 100,
            "storage": "20 GB",
            "storage_value": 20,
            "type": "SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "email": "Free Email",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Weekly Backups",
            "popular": True,
            "best_for": "Small businesses",
            "bonus": "3 months free"
        },
        "Business": {
            "price": 249,
            "regular_price": 699,
            "websites": 100,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "email": "Free Email",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Growing businesses",
            "bonus": "3 months free"
        },
        "Cloud Startup": {
            "price": 599,
            "regular_price": 1699,
            "websites": 300,
            "storage": "200 GB",
            "storage_value": 200,
            "type": "SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "email": "Free Email",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "High-traffic websites",
            "bonus": "3 months free"
        }
    },
    "bluehost": {
        "Shared": {
            "price": 169,
            "regular_price": 299,
            "websites": 1,
            "storage": "50 GB",
            "storage_value": 50,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "5 Email Accounts",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Basic Backup",
            "popular": True,
            "best_for": "Beginners"
        },
        "VPS": {
            "price": 1749,
            "regular_price": 1859,
            "websites": "Unlimited",
            "storage": "30 GB",
            "storage_value": 30,
            "type": "SSD",
            "bandwidth": "1 TB",
            "bandwidth_value": 1000,
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backup",
            "popular": False,
            "best_for": "Growing websites"
        },
        "Dedicated": {
            "price": 4859,
            "regular_price": 6719,
            "websites": "Unlimited",
            "storage": "500 GB",
            "storage_value": 500,
            "type": "SSD",
            "bandwidth": "5 TB",
            "bandwidth_value": 5000,
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backup",
            "popular": False,
            "best_for": "High-traffic websites"
        }
    },
    "godaddy": {
        "Starter": {
            "price": 89,
            "regular_price": 249,
            "websites": 1,
            "storage": "10 GB",
            "storage_value": 10,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "None",
            "free_domain": False,
            "ssl": "Not Included",
            "cpanel": True,
            "backup": "Basic Backup",
            "popular": False,
            "best_for": "Beginners",
            "term": "3-year"
        },
        "Economy": {
            "price": 219,
            "regular_price": 499,
            "websites": 1,
            "storage": "25 GB",
            "storage_value": 25,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Free Email",
            "free_domain": True,
            "ssl": "Free SSL (1 year)",
            "cpanel": True,
            "backup": "Basic Backup",
            "popular": False,
            "best_for": "Personal websites",
            "term": "3-year"
        },
        "Deluxe": {
            "price": 329,
            "regular_price": 699,
            "websites": 10,
            "storage": "50 GB",
            "storage_value": 50,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Free Email",
            "free_domain": True,
            "ssl": "Unlimited Free SSL",
            "cpanel": True,
            "backup": "Basic Backup",
            "popular": True,
            "best_for": "Small businesses",
            "term": "3-year"
        }
    },
    "bigrock": {
        "Starter": {
            "price": 69,
            "regular_price": 159,
            "websites": 1,
            "storage": "20 GB",
            "storage_value": 20,
            "type": "SSD",
            "bandwidth": "100 GB",
            "bandwidth_value": 100,
            "email": "5 Email Accounts",
            "free_domain": False,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Growing businesses"
        },
        "Advanced": {
            "price": 159,
            "regular_price": 279,
            "websites": 1,
            "storage": "Unmetered",
            "storage_value": float('inf'),
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "Developed establishments"
        },
        "Pro": {
            "price": 199,
            "regular_price": 329,
            "websites": "Unlimited",
            "storage": "Unmetered",
            "storage_value": float('inf'),
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Established organizations"
        },
        "Ultimate": {
            "price": 249,
            "regular_price": 469,
            "websites": "Unlimited",
            "storage": "Unmetered",
            "storage_value": float('inf'),
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Premium SSL",
            "cpanel": True,
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Large-scale companies"
        }
    },
    "namecheap": {
        "Stellar": {
            "price": 127,
            "regular_price": 384,
            "websites": 3,
            "storage": "20 GB",
            "storage_value": 20,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "30 Mailboxes",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "Basic Backup",
            "popular": False,
            "best_for": "Small websites",
            "features": "AI Website Builder, AI Tools"
        },
        "Stellar Plus": {
            "price": 204,
            "regular_price": 556,
            "websites": "Unlimited",
            "storage": "Unmetered",
            "storage_value": float('inf'),
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "AutoBackup",
            "popular": True,
            "best_for": "Multiple websites",
            "features": "AI Website Builder, AI Tools"
        },
        "Stellar Business": {
            "price": 427,
            "regular_price": 813,
            "websites": "Unlimited",
            "storage": "50 GB",
            "storage_value": 50,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "cpanel": True,
            "backup": "AutoBackup & Cloud Storage",
            "popular": False,
            "best_for": "Business websites",
            "features": "AI Website Builder, AI Tools"
        }
    }
}

# VPS hosting plans data
vps_data = {
    "hostinger": {
        "KVM 2": {
            "price": 749,
            "regular_price": 1599,
            "cpu_cores": 2,
            "ram": 8,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "NVMe",
            "bandwidth": "8 TB",
            "bandwidth_value": 8000,
            "email": "Available",
            "free_domain": False,
            "ssl": "Free SSL",
            "backup": "Free weekly backups",
            "popular": True,
            "best_for": "Growing applications"
        }
    },
    "bluehost": {
        "Enhanced NVMe 8": {
            "price": 6299,
            "regular_price": 8695,
            "cpu_cores": 4,
            "ram": 8,
            "storage": "200 GB",
            "storage_value": 200,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "email": "Available",
            "free_domain": False,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "More storage and customization"
        }
    },
    "bigrock": {
        "NVMe 8": {
            "price": 6838,
            "regular_price": 7500,
            "cpu_cores": 4,
            "ram": 8,
            "storage": "200 GB",
            "storage_value": 200,
            "type": "NVMe",
            "bandwidth": "3 TB",
            "bandwidth_value": 3000,
            "email": "Available",
            "free_domain": False,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "Business applications"
        }
    },
    "namecheap": {
        "Quasar": {
            "price": 1409,
            "regular_price": 1409,
            "cpu_cores": 4,
            "ram": 6,
            "storage": "120 GB",
            "storage_value": 120,
            "type": "SSD RAID 10",
            "bandwidth": "3 TB",
            "bandwidth_value": 3000,
            "email": "Available",
            "free_domain": False,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "Medium VPS projects"
        }
    }
}

dedicated_data = {
    "bigrock": {
        "Mach-1 SSD": {
            "price": 7699,
            "regular_price": 10999,
            "cpu_cores": 8,
            "cpu_speed": "2.20GHz Octa Core",
            "ram": 16,
            "storage": "500 GB",
            "storage_value": 500,
            "type": "SSD (RAID 1)",
            "bandwidth": "5 TB",
            "bandwidth_value": 5000,
            "os": "Linux",
            "ips": "2 IPs",
            "migration": "Free Website Migration",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Growing businesses"
        },
        "Mach-2 SSD": {
            "price": 8399,
            "regular_price": 11999,
            "cpu_cores": 8,
            "cpu_speed": "2.20GHz Octa Core",
            "ram": 28,
            "storage": "1000 GB",
            "storage_value": 1000,
            "type": "SSD (RAID 1)",
            "bandwidth": "10 TB",
            "bandwidth_value": 10000,
            "os": "Linux",
            "ips": "2 IPs",
            "migration": "Free Website Migration",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "Developed enterprises"
        },
        "Mach-3 SSD": {
            "price": 10499,
            "regular_price": 14999,
            "cpu_cores": 8,
            "cpu_speed": "2.20GHz Octa Core",
            "ram": 60,
            "storage": "1790 GB",
            "storage_value": 1790,
            "type": "SSD (RAID 1)",
            "bandwidth": "15 TB",
            "bandwidth_value": 15000,
            "os": "Linux",
            "ips": "2 IPs",
            "migration": "Free Website Migration",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Established organisations"
        }
    },
    "bluehost": {
        "Standard NVMe 32": {
            "price": 12903,
            "regular_price": 17163,
            "cpu_cores": 8,
            "cpu_speed": "8 CPU cores",
            "ram": 32,
            "storage": "1000 GB",
            "storage_value": 1000,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "os": "Linux/Windows",
            "ips": "3 IPs",
            "migration": "Free Site Migration Tool",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Ultimate performance"
        },
        "Enhanced NVMe 64": {
            "price": 19704,
            "regular_price": 24536,
            "cpu_cores": 16,
            "cpu_speed": "16 CPU cores",
            "ram": 64,
            "storage": "2000 GB",
            "storage_value": 2000,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "os": "Linux/Windows",
            "ips": "3 IPs",
            "migration": "Free Site Migration Tool",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": True,
            "best_for": "More storage and power"
        },
        "Premium NVMe 128": {
            "price": 28206,
            "regular_price": 35275,
            "cpu_cores": 32,
            "cpu_speed": "32 CPU cores",
            "ram": 128,
            "storage": "3000 GB",
            "storage_value": 3000,
            "type": "NVMe",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "os": "Linux/Windows",
            "ips": "3 IPs",
            "migration": "Free Site Migration Tool",
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "popular": False,
            "best_for": "Maximum power and resources"
        }
    }
}

## Cloud Hosting Plans - COMPREHENSIVE UPDATE
cloud_hosting_data = {
    "bigrock": {
        "Starter SSD": {
            "price": 799,
            "regular_price": 769,
            "cpu_cores": 2,
            "ram": 2,
            "storage": "25 GB",
            "storage_value": 25,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": 1,
            "email": "75 Email Accounts",
            "email_accounts": 75,
            "free_domain": False,
            "ssl": "Free Let's Encrypt SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "anti_malware": True,
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Small business websites"
        },
        "Advanced SSD": {
            "price": 999,
            "regular_price": 1099,
            "cpu_cores": 4,
            "ram": 4,
            "storage": "50 GB",
            "storage_value": 50,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": 50,
            "email": "100 Email Accounts",
            "email_accounts": 100,
            "free_domain": False,
            "ssl": "Free Let's Encrypt SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "anti_malware": True,
            "dedicated_ip": False,
            "popular": True,
            "best_for": "Growing businesses with multiple sites"
        },
        "Business SSD": {
            "price": 1399,
            "regular_price": 1269,
            "cpu_cores": 6,
            "ram": 6,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": 100,
            "email": "150 Email Accounts",
            "email_accounts": 150,
            "free_domain": False,
            "ssl": "Free Premium SSL for 1 Year",
            "backup": "Daily Backups",
            "cpanel": True,
            "anti_malware": True,
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Large-scale business operations"
        }
    },
    "hostinger": {
        "Cloud Startup": {
            "price": 999,
            "regular_price": 1999,
            "cpu_cores": 2,
            "ram": 3,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "NVMe",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": 100,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "nodejs": "5 Node.js web apps",
            "php_workers": 100,
            "inodes": "2,000,000",
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Business and eCommerce websites"
        },
        "Cloud Professional": {
            "price": 1499,
            "regular_price": 2999,
            "cpu_cores": 4,
            "ram": 6,
            "storage": "200 GB",
            "storage_value": 200,
            "type": "NVMe",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": 100,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "nodejs": "5 Node.js web apps",
            "php_workers": 200,
            "inodes": "3,000,000",
            "dedicated_ip": True,
            "popular": True,
            "best_for": "Resource-intensive applications"
        },
        "Cloud Enterprise": {
            "price": 1999,
            "regular_price": 3999,
            "cpu_cores": 6,
            "ram": 12,
            "storage": "300 GB",
            "storage_value": 300,
            "type": "NVMe",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": 100,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "nodejs": "5 Node.js web apps",
            "php_workers": 300,
            "inodes": "4,000,000",
            "dedicated_ip": True,
            "popular": False,
            "best_for": "High-traffic enterprise websites"
        }
    },
    "verpex": {
        "Bronze": {
            "price": 248,
            "regular_price": 498,
            "cpu_cores": 2,
            "ram": 2,
            "storage": "30 GB",
            "storage_value": 30,
            "type": "NVMe SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": 1,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL Certificates",
            "backup": "Free Daily Backups",
            "cpanel": "cPanel Control Panel",
            "litespeed": True,
            "wordpress": "1-click WordPress Installation",
            "migrations": "Free Migrations",
            "money_back": "45 Day Money Back Guarantee",
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Single website management"
        },
        "Silver": {
            "price": 414,
            "regular_price": 830,
            "cpu_cores": 4,
            "ram": 4,
            "storage": "50 GB",
            "storage_value": 50,
            "type": "NVMe SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": 100,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL Certificates",
            "backup": "Free Daily Backups",
            "cpanel": "cPanel Control Panel",
            "litespeed": True,
            "wordpress": "1-click WordPress Installation",
            "migrations": "Free Migrations",
            "money_back": "45 Day Money Back Guarantee",
            "dedicated_ip": False,
            "popular": True,
            "best_for": "Multiple websites with superior performance"
        },
        "Gold": {
            "price": 746,
            "regular_price": 1245,
            "cpu_cores": 6,
            "ram": 8,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "NVMe SSD",
            "bandwidth": "Unlimited",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL Certificates",
            "backup": "Free Daily Backups",
            "cpanel": "cPanel Control Panel",
            "litespeed": True,
            "wordpress": "1-click WordPress Installation",
            "migrations": "Free Migrations",
            "money_back": "45 Day Money Back Guarantee",
            "dedicated_ip": True,
            "popular": False,
            "best_for": "Unlimited sites with maximum resources"
        }
    },
    "bluehost": {
        "Cloud Essentials": {
            "price": 5749,
            "regular_price": 6999,
            "cpu_cores": 4,
            "ram": 4,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Growing cloud-based websites"
        },
        "Cloud Performance": {
            "price": 8999,
            "regular_price": 10999,
            "cpu_cores": 6,
            "ram": 8,
            "storage": "200 GB",
            "storage_value": 200,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": True,
            "popular": True,
            "best_for": "High-performance cloud hosting"
        },
        "Cloud Ultimate": {
            "price": 12999,
            "regular_price": 15999,
            "cpu_cores": 8,
            "ram": 16,
            "storage": "300 GB",
            "storage_value": 300,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": True,
            "popular": False,
            "best_for": "Enterprise cloud solutions"
        }
    },
    "godaddy": {
        "Cloud Economy": {
            "price": 4999,
            "regular_price": 6999,
            "cpu_cores": 4,
            "ram": 4,
            "storage": "100 GB",
            "storage_value": 100,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": 1,
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": False,
            "popular": False,
            "best_for": "Small to medium cloud sites"
        },
        "Cloud Deluxe": {
            "price": 8999,
            "regular_price": 11999,
            "cpu_cores": 6,
            "ram": 8,
            "storage": "150 GB",
            "storage_value": 150,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": False,
            "popular": True,
            "best_for": "Multiple cloud websites"
        },
        "Cloud Ultimate": {
            "price": 12999,
            "regular_price": 15999,
            "cpu_cores": 8,
            "ram": 16,
            "storage": "250 GB",
            "storage_value": 250,
            "type": "SSD",
            "bandwidth": "Unmetered",
            "bandwidth_value": float('inf'),
            "websites": "Unlimited",
            "email": "Unlimited",
            "email_accounts": "Unlimited",
            "free_domain": True,
            "ssl": "Free SSL",
            "backup": "Daily Backups",
            "cpanel": True,
            "dedicated_ip": True,
            "popular": False,
            "best_for": "Large-scale cloud applications"
        }
    }
}

# Updated Cloud Hosting Buy Links

# Buy Links
buy_links = {
    'hostinger': {
        'Single': 'https://www.hostinger.com/web-hosting',
        'Premium': 'https://www.hostinger.com/web-hosting',
        'Cloud Startup':'https://www.hostinger.com/web-hosting',
        'Business':'https://www.hostinger.com/web-hosting'
    },
    'bluehost': {
        'Shared': 'https://www.bluehost.in/hosting/shared',
        'Dedicated':'https://www.bluehost.in/hosting/shared'
    },
    'namecheap':{
        'Stellar':'https://www.namecheap.com/hosting/shared/',
        'Stellar Plus':'https://www.namecheap.com/hosting/shared/',
        'Stellar Business':'https://www.namecheap.com/hosting/shared/'
    },
    'bigrock':{
    'Starter':'https://www.bigrock.in/web-hosting/linux-hosting',
    'Pro':'https://www.bigrock.in/web-hosting/linux-hosting',
    'Ultimate':'https://www.bigrock.in/web-hosting/linux-hosting'
    },
    'goddady':{
        'Deluxe':'https://www.godaddy.com/en-in/hosting/web-hosting',
        'Economy':'https://www.godaddy.com/en-in/hosting/web-hosting'
        'https://www.godaddy.com/en-in/hosting/web-hosting'
        'https://www.godaddy.com/en-in/hosting/web-hosting'
    }
}

vps_buy_links = {
    'hostinger': {
        'KVM 2': 'https://www.hostinger.in/vps-hosting'
    },
    'bluehost': {
        'Enhanced NVMe 8': 'https://www.bluehost.in/hosting/vps'
    },
    'namecheap':{
    'Quasar':'https://www.namecheap.com/hosting/vps/'
    }
}

dedicated_buy_links = {
    'bigrock': {
        'Mach-1 SSD': 'https://www.bigrock.in/managed-dedicated-server',
        'Mach-2 SSD': 'https://www.bigrock.in/managed-dedicated-server',
        'Mach-3 SSD': 'https://www.bigrock.in/managed-dedicated-server'
    },
    'bluehost': {
        'Standard NVMe 32': 'https://www.bluehost.in/hosting/dedicated',
        'Enhanced NVMe 64': 'https://www.bluehost.in/hosting/dedicated',
        'Premium NVMe 128': 'https://www.bluehost.in/hosting/dedicated'
    }
}

cloud_hosting_buy_links = {
    'bigrock': {
        'Starter SSD': 'https://www.bigrock.in/cloud-hosting',
        'Advanced SSD': 'https://www.bigrock.in/cloud-hosting',
        'Business SSD': 'https://www.bigrock.in/cloud-hosting'
    },
    'hostinger': {
        'Cloud Startup': 'https://www.hostinger.in/cloud-hosting',
        'Cloud Professional': 'https://www.hostinger.in/cloud-hosting',
        'Cloud Enterprise': 'https://www.hostinger.in/cloud-hosting'
    },
    'verpex': {
        'Bronze': 'https://verpex.com/cloud-hosting',
        'Silver': 'https://verpex.com/cloud-hosting',
        'Gold': 'https://verpex.com/cloud-hosting'
    },
    'bluehost': {
        'Cloud Essentials': 'https://www.bluehost.in/hosting/cloud',
        'Cloud Performance': 'https://www.bluehost.in/hosting/cloud',
        'Cloud Ultimate': 'https://www.bluehost.in/hosting/cloud'
    },
    'godaddy': {
        'Cloud Economy': 'https://www.godaddy.com/hosting/cloud-hosting',
        'Cloud Deluxe': 'https://www.godaddy.com/hosting/cloud-hosting',
        'Cloud Ultimate': 'https://www.godaddy.com/hosting/cloud-hosting'
    }
}


# [Keep all your existing data: hosting_data, vps_data, dedicated_data, cloud_hosting_data]
# [Keep all your existing buy_links dictionaries]
# def calculate_score(plan, budget, websites, storage, need_email, need_domain, need_ssl):
#     """Calculate a score for how well a plan matches requirements"""
#     score = 0
    
#     # IMPROVED: Better value for money calculation
#     if plan['price'] <= budget:
#         value_ratio = 1 - (plan['price'] / budget)
#         score += value_ratio * 30
#     elif plan['price'] <= budget * 1.5:
#         # Still give some score if within 50% of budget
#         value_ratio = 0.5 - ((plan['price'] - budget) / budget * 0.5)
#         score += value_ratio * 30
#     else:
#         # Heavy penalty for too expensive
#         score -= 10
    
#     # Storage match
#     if plan['storage_value'] == float('inf'):
#         storage_score = 1
#     else:
#         if plan['storage_value'] >= storage:
#             storage_ratio = min(plan['storage_value'] / storage, 2) / 2
#             storage_score = storage_ratio
#         else:
#             storage_score = 0.3
#     score += storage_score * 20
    
#     # Website allowance (only for shared hosting and cloud)
#     if 'websites' in plan:
#         if plan['websites'] == "Unlimited":
#             website_score = 1
#         else:
#             if plan['websites'] >= websites:
#                 website_ratio = min(plan['websites'] / websites, 2) / 2
#                 website_score = website_ratio
#             else:
#                 website_score = 0.5
#         score += website_score * 20
#     else:
#         score += 20  # Full score for VPS/Dedicated plans
    
#     # Features - only count if user requested them
#     feature_score = 0
#     features_requested = 0
    
#     if need_domain:
#         features_requested += 1
#         if plan.get('free_domain', False):
#             feature_score += 1
            
#     if need_ssl:
#         features_requested += 1
#         if 'SSL' in plan.get('ssl', ''):
#             feature_score += 1
            
#     if need_email:
#         features_requested += 1
#         if plan.get('email', 'None') != "None":
#             feature_score += 1
    
#     # Normalize feature score
#     if features_requested > 0:
#         feature_score = (feature_score / features_requested) * 30
#     else:
#         feature_score = 30  # Full score if no features requested
        
#     score += feature_score
    
#     return score
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    featured_image = db.Column(db.String(300))
    published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50))
    company = db.Column(db.String(120))
    service = db.Column(db.String(100))
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<ContactSubmission {self.email}>'


class HostingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(120), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    hosting_type = db.Column(db.String(30), nullable=False, index=True)
    price = db.Column(db.Integer, nullable=False)
    regular_price = db.Column(db.Integer, nullable=False)
    billing_text = db.Column(db.String(120))
    storage = db.Column(db.String(60), nullable=False)
    storage_value = db.Column(db.Float)
    storage_type = db.Column(db.String(30))
    bandwidth = db.Column(db.String(60), nullable=False)
    bandwidth_value = db.Column(db.Float)
    websites_value = db.Column(db.Integer)
    websites_text = db.Column(db.String(60))
    websites_unlimited = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120))
    free_domain = db.Column(db.Boolean, default=False)
    ssl = db.Column(db.String(120))
    backup = db.Column(db.String(120))
    best_for = db.Column(db.String(120))
    buy_link = db.Column(db.String(300))
    cpu_cores = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    ips = db.Column(db.String(120))
    migration = db.Column(db.String(120))
    uptime = db.Column(db.String(60))
    money_back = db.Column(db.String(60))
    popular = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('provider', 'hosting_type', 'name', name='uq_hosting_plan_provider_type_name'),
    )

    def __repr__(self):
        return f'<HostingPlan {self.provider} {self.name}>'

    def websites_display(self):
        if self.websites_unlimited:
            return 'Unlimited'
        if self.websites_value is not None:
            return self.websites_value
        if self.websites_text:
            return self.websites_text
        return 0

    def to_plan_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'regular_price': self.regular_price or self.price,
            'billing_text': self.billing_text or f'₹{self.price}/mo billed annually',
            'storage': self.storage,
            'storage_value': self.storage_value if self.storage_value is not None else 0,
            'type': self.storage_type or '',
            'bandwidth': self.bandwidth,
            'bandwidth_value': self.bandwidth_value if self.bandwidth_value is not None else 0,
            'websites': self.websites_display(),
            'email': self.email or 'None',
            'free_domain': bool(self.free_domain),
            'ssl': self.ssl or 'No SSL included',
            'backup': self.backup or 'No backup details provided',
            'popular': bool(self.popular),
            'best_for': self.best_for or 'General workloads',
            'buy_link': self.buy_link or '#',
            'cpu_cores': self.cpu_cores or 0,
            'ram': self.ram or 0,
            'ips': self.ips or 'Standard IP allocation',
            'migration': self.migration or 'Migration support available',
            'uptime': self.uptime or '99.9% uptime',
            'money_back': self.money_back or '30 day money-back',
        }


def parse_numeric_value(value):
    if value in (None, ''):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    normalized = str(value).strip().lower()
    if normalized in {'inf', 'infinity', 'unlimited', 'unmetered'}:
        return float('inf')
    return float(normalized)


def parse_optional_int(value):
    if value in (None, ''):
        return None
    return int(value)


def default_money_back_for_type(hosting_type):
    return '7 day money-back' if hosting_type in {'vps', 'dedicated'} else '30 day money-back'


def get_budget_rule(hosting_type):
    return PLAN_BUDGET_RULES.get(hosting_type, PLAN_BUDGET_RULES['shared'])


def build_plan_record(provider, hosting_type, plan_name, plan_data, link, sort_order):
    websites = plan_data.get('websites')
    websites_unlimited = isinstance(websites, str) and websites.strip().lower() == 'unlimited'
    websites_value = None
    websites_text = None

    if websites_unlimited:
        websites_text = 'Unlimited'
    elif isinstance(websites, int):
        websites_value = websites
    elif websites not in (None, ''):
        try:
            websites_value = int(websites)
        except (TypeError, ValueError):
            websites_text = str(websites)

    return HostingPlan(
        provider=provider,
        name=plan_name,
        hosting_type=hosting_type,
        price=int(plan_data.get('price') or 0),
        regular_price=int(plan_data.get('regular_price') or plan_data.get('price') or 0),
        billing_text=f"₹{plan_data.get('price')}/mo billed annually",
        storage=str(plan_data.get('storage') or ''),
        storage_value=parse_numeric_value(plan_data.get('storage_value')),
        storage_type=str(plan_data.get('type') or ''),
        bandwidth=str(plan_data.get('bandwidth') or ''),
        bandwidth_value=parse_numeric_value(plan_data.get('bandwidth_value')),
        websites_value=websites_value,
        websites_text=websites_text,
        websites_unlimited=websites_unlimited,
        email=str(plan_data.get('email') or ''),
        free_domain=bool(plan_data.get('free_domain')),
        ssl=str(plan_data.get('ssl') or ''),
        backup=str(plan_data.get('backup') or ''),
        best_for=str(plan_data.get('best_for') or ''),
        buy_link=link or '#',
        cpu_cores=parse_optional_int(plan_data.get('cpu_cores')),
        ram=parse_optional_int(plan_data.get('ram')),
        ips=str(plan_data.get('ips') or ''),
        migration=str(plan_data.get('migration') or ''),
        uptime=str(plan_data.get('uptime') or '99.9% uptime'),
        money_back=str(plan_data.get('money_back') or default_money_back_for_type(hosting_type)),
        popular=bool(plan_data.get('popular')),
        active=True,
        sort_order=sort_order,
    )


def seed_default_hosting_plans():
    if HostingPlan.query.count():
        return 0

    sources = [
        ('shared', hosting_data, buy_links),
        ('vps', vps_data, vps_buy_links),
        ('cloud', cloud_hosting_data, cloud_hosting_buy_links),
        ('dedicated', dedicated_data, dedicated_buy_links),
    ]

    created = 0
    for hosting_type, plan_source, link_source in sources:
        for provider, plans in plan_source.items():
            for plan_name, plan_data in plans.items():
                db.session.add(
                    build_plan_record(
                        provider=provider,
                        hosting_type=hosting_type,
                        plan_name=plan_name,
                        plan_data=plan_data,
                        link=link_source.get(provider, {}).get(plan_name, '#'),
                        sort_order=created,
                    )
                )
                created += 1

    if created:
        db.session.commit()
    return created


def ensure_database_ready():
    with app.app_context():
        db.create_all()
        seed_default_hosting_plans()


def fetch_plan_catalog(hosting_type):
    return HostingPlan.query.filter_by(hosting_type=hosting_type, active=True).order_by(
        HostingPlan.popular.desc(),
        HostingPlan.sort_order.asc(),
        HostingPlan.price.asc(),
        HostingPlan.provider.asc(),
    ).all()


def plan_matches_requirements(plan, hosting_type, websites, storage, budget, budget_multiplier):
    storage_ok = (
        plan['storage_value'] == float('inf') or
        plan['storage_value'] >= storage * 0.5
    )
    price_ok = plan['price'] <= budget * budget_multiplier

    if hosting_type in {'vps', 'dedicated'}:
        return price_ok and storage_ok

    websites_value = plan.get('websites')
    websites_ok = (
        websites_value == 'Unlimited' or
        (isinstance(websites_value, int) and websites_value >= websites)
    )

    if hosting_type == 'cloud':
        return price_ok and storage_ok and websites_ok

    return price_ok and storage_ok and websites_ok


def find_matching_plans(hosting_type, websites, storage, budget, need_email, need_domain, need_ssl):
    rule = get_budget_rule(hosting_type)
    matching_plans = []

    for record in fetch_plan_catalog(hosting_type):
        plan = record.to_plan_dict()
        if not plan_matches_requirements(plan, hosting_type, websites, storage, budget, rule['budget_multiplier']):
            continue

        matching_plans.append({
            'provider': record.provider,
            'plan_name': record.name,
            'plan': plan,
            'score': calculate_score(plan, budget, websites, storage, need_email, need_domain, need_ssl),
        })

    matching_plans.sort(key=lambda item: item['score'], reverse=True)
    return matching_plans, rule


def plan_form_data(plan=None):
    if not plan:
        return {
            'provider': '',
            'name': '',
            'hosting_type': 'shared',
            'price': '',
            'regular_price': '',
            'billing_text': '',
            'storage': '',
            'storage_value': '',
            'storage_type': 'SSD',
            'bandwidth': '',
            'bandwidth_value': '',
            'websites_value': '',
            'websites_text': '',
            'websites_unlimited': False,
            'email': '',
            'free_domain': False,
            'ssl': '',
            'backup': '',
            'best_for': '',
            'buy_link': '',
            'cpu_cores': '',
            'ram': '',
            'ips': '',
            'migration': '',
            'uptime': '99.9% uptime',
            'money_back': '',
            'popular': False,
            'active': True,
            'sort_order': 0,
        }

    return {
        'provider': plan.provider,
        'name': plan.name,
        'hosting_type': plan.hosting_type,
        'price': plan.price,
        'regular_price': plan.regular_price,
        'billing_text': plan.billing_text or '',
        'storage': plan.storage,
        'storage_value': '' if plan.storage_value is None else ('Infinity' if plan.storage_value == float('inf') else int(plan.storage_value) if float(plan.storage_value).is_integer() else plan.storage_value),
        'storage_type': plan.storage_type or '',
        'bandwidth': plan.bandwidth,
        'bandwidth_value': '' if plan.bandwidth_value is None else ('Infinity' if plan.bandwidth_value == float('inf') else int(plan.bandwidth_value) if float(plan.bandwidth_value).is_integer() else plan.bandwidth_value),
        'websites_value': '' if plan.websites_value is None else plan.websites_value,
        'websites_text': plan.websites_text or '',
        'websites_unlimited': bool(plan.websites_unlimited),
        'email': plan.email or '',
        'free_domain': bool(plan.free_domain),
        'ssl': plan.ssl or '',
        'backup': plan.backup or '',
        'best_for': plan.best_for or '',
        'buy_link': plan.buy_link or '',
        'cpu_cores': '' if plan.cpu_cores is None else plan.cpu_cores,
        'ram': '' if plan.ram is None else plan.ram,
        'ips': plan.ips or '',
        'migration': plan.migration or '',
        'uptime': plan.uptime or '',
        'money_back': plan.money_back or '',
        'popular': bool(plan.popular),
        'active': bool(plan.active),
        'sort_order': plan.sort_order or 0,
    }


def upsert_plan_from_form(plan=None):
    provider = request.form.get('provider', '').strip()
    name = request.form.get('name', '').strip()
    hosting_type = request.form.get('hosting_type', 'shared').strip()
    storage = request.form.get('storage', '').strip()
    bandwidth = request.form.get('bandwidth', '').strip()

    if not provider or not name or not storage or not bandwidth:
        raise ValueError('Provider, plan name, storage, and bandwidth are required.')
    if hosting_type not in HOSTING_TYPE_LABELS:
        raise ValueError('Select a valid hosting type.')

    price = int(request.form.get('price', '0') or 0)
    if price <= 0:
        raise ValueError('Monthly price must be greater than 0.')

    record = plan or HostingPlan()
    record.provider = provider
    record.name = name
    record.hosting_type = hosting_type
    record.price = price
    record.regular_price = int(request.form.get('regular_price', str(price)) or price)
    record.billing_text = request.form.get('billing_text', '').strip() or f'₹{price}/mo billed annually'
    record.storage = storage
    record.storage_value = parse_numeric_value(request.form.get('storage_value', '').strip())
    record.storage_type = request.form.get('storage_type', '').strip()
    record.bandwidth = bandwidth
    record.bandwidth_value = parse_numeric_value(request.form.get('bandwidth_value', '').strip())
    record.websites_unlimited = request.form.get('websites_unlimited') == 'on'
    record.websites_value = None if record.websites_unlimited else parse_optional_int(request.form.get('websites_value', '').strip())
    record.websites_text = '' if record.websites_unlimited else request.form.get('websites_text', '').strip()
    record.email = request.form.get('email', '').strip()
    record.free_domain = request.form.get('free_domain') == 'on'
    record.ssl = request.form.get('ssl', '').strip()
    record.backup = request.form.get('backup', '').strip()
    record.best_for = request.form.get('best_for', '').strip()
    record.buy_link = request.form.get('buy_link', '').strip() or '#'
    record.cpu_cores = parse_optional_int(request.form.get('cpu_cores', '').strip())
    record.ram = parse_optional_int(request.form.get('ram', '').strip())
    record.ips = request.form.get('ips', '').strip()
    record.migration = request.form.get('migration', '').strip()
    record.uptime = request.form.get('uptime', '').strip() or '99.9% uptime'
    record.money_back = request.form.get('money_back', '').strip() or default_money_back_for_type(hosting_type)
    record.popular = request.form.get('popular') == 'on'
    record.active = request.form.get('active') == 'on'
    record.sort_order = int(request.form.get('sort_order', '0') or 0)

    if record.websites_unlimited:
        record.websites_text = 'Unlimited'
    elif record.websites_value is None and record.websites_text:
        match = re.search(r'(\d+)', record.websites_text)
        if match:
            record.websites_value = int(match.group(1))

    return record

# ADMIN AUTHENTICATION DECORATOR
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# HELPER FUNCTION TO CREATE SLUG
def create_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


ensure_database_ready()

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return render_template('home.html')

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')


@app.route('/web-hosting-comparison-tool-2026')
def hosting_comparison_2026():
    return render_template('hosting_comparison_2026.html')

@app.route('/Cloud_&_Infrastructure_Strategy')
def service1():
    return render_template('service1.html')

@app.route('/Migration_Services')
def service2():
    return render_template('service2.html')

@app.route('/Managed_Services')
def service3():
    return render_template('service3.html')

@app.route('/Digital_Security_&_Compliance')
def service4():
    return render_template('service4.html')

@app.route('/Digital_Transformation_&_Future-Proofing')
def service5():
    return render_template('service5.html')

# # Add route in app.py
# @app.route('/robots.txt')
# def robots():
#     return send_from_directory('static', 'robots.txt')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with persistent lead capture."""
    form_data = {
        'name': '',
        'email': '',
        'phone': '',
        'company': '',
        'service': '',
        'subject': '',
        'message': ''
    }

    if request.method == 'POST':
        form_data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip().lower(),
            'phone': request.form.get('phone', '').strip(),
            'company': request.form.get('company', '').strip(),
            'service': request.form.get('service', '').strip(),
            'subject': request.form.get('subject', '').strip(),
            'message': request.form.get('message', '').strip()
        }

        if not form_data['name'] or not form_data['email'] or not form_data['subject'] or not form_data['message']:
            flash('Please complete all required fields.', 'error')
            return render_template('contact.html', form_data=form_data)

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', form_data['email']):
            flash('Please enter a valid email address.', 'error')
            return render_template('contact.html', form_data=form_data)

        submission = ContactSubmission(**form_data)
        try:
            db.session.add(submission)
            db.session.commit()
            flash('Thanks for reaching out. Your message has been saved and our team will reply soon.', 'success')
            return redirect(url_for('contact'))
        except Exception:
            db.session.rollback()
            flash('We could not submit your message right now. Please try again in a moment.', 'error')

    return render_template('contact.html', form_data=form_data)

def calculate_score(plan, budget, websites, storage, need_email, need_domain, need_ssl):
    """Calculate a score for how well a plan matches requirements - FIXED"""
    score = 0
    
    # FIXED: Better value for money calculation
    if plan['price'] <= budget:
        value_ratio = 1 - (plan['price'] / budget)
        score += value_ratio * 30
    elif plan['price'] <= budget * 2:
        # Give partial score if within 2x budget
        value_ratio = 0.3
        score += value_ratio * 30
    else:
        # Still give some score for expensive plans
        score += 5
    
    # Storage match - IMPROVED
    if plan['storage_value'] == float('inf'):
        storage_score = 1
    else:
        if plan['storage_value'] >= storage:
            storage_ratio = min(plan['storage_value'] / max(storage, 1), 2) / 2
            storage_score = max(storage_ratio, 0.5)  # At least 50% score
        else:
            storage_score = 0.3  # Still give some score
    score += storage_score * 20
    
    # Website allowance - IMPROVED
    if 'websites' in plan:
        if plan['websites'] == "Unlimited":
            website_score = 1
        else:
            if plan['websites'] >= websites:
                website_ratio = min(plan['websites'] / max(websites, 1), 2) / 2
                website_score = max(website_ratio, 0.5)  # At least 50% score
            else:
                website_score = 0.3  # Still give some score
        score += website_score * 20
    else:
        score += 20  # Full score for VPS/Dedicated/Cloud
    
    # Features - BONUS points (not penalties)
    feature_bonus = 0
    if need_domain and plan.get('free_domain', False):
        feature_bonus += 10
    if need_ssl and 'SSL' in plan.get('ssl', ''):
        feature_bonus += 10
    if need_email and plan.get('email', 'None') != "None":
        feature_bonus += 10
        
    score += feature_bonus  # Bonus instead of weighted
    
    return max(score, 10)  # Ensure minimum score of 10


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """Main calculator page backed by database plans."""
    form_data = {
        'websites': 1,
        'storage': 10,
        'budget': 200,
        'email': False,
        'domain': False,
        'ssl': False,
        'custom_plan': False,
        'hosting_type': 'shared',
        'cpu_cores': 2,
        'ram': 4,
    }
    show_results = False
    results = None
    error = None

    if request.method == 'POST':
        try:
            try:
                websites = int(request.form.get('websites', 1))
            except ValueError:
                websites = 1

            try:
                storage = int(request.form.get('storage', 10))
            except ValueError:
                storage = 10

            try:
                budget = int(request.form.get('budget', 200))
            except ValueError:
                budget = 200

            try:
                cpu_cores = int(request.form.get('cpu_cores', 2))
            except ValueError:
                cpu_cores = 2

            try:
                ram = int(request.form.get('ram', 4))
            except ValueError:
                ram = 4

            form_data['websites'] = websites
            form_data['storage'] = storage
            form_data['budget'] = budget
            form_data['cpu_cores'] = cpu_cores
            form_data['ram'] = ram
            form_data['email'] = request.form.get('email') == 'on'
            form_data['domain'] = request.form.get('domain') == 'on'
            form_data['ssl'] = request.form.get('ssl') == 'on'
            form_data['custom_plan'] = request.form.get('custom_plan') == 'on'
            form_data['hosting_type'] = request.form.get('hosting_type', 'shared')

            matching_plans, rule = find_matching_plans(
                hosting_type=form_data['hosting_type'],
                websites=websites,
                storage=storage,
                budget=budget,
                need_email=form_data['email'],
                need_domain=form_data['domain'],
                need_ssl=form_data['ssl'],
            )

            results = {
                'best_plan': matching_plans[0] if matching_plans else None,
                'all_plans': [
                    {
                        'provider': item['provider'],
                        'plan_name': item['plan_name'],
                        'plan': item['plan'],
                        'score': round(min(item['score'], 100) / 10, 1),
                    }
                    for item in matching_plans[:12]
                ],
                'count': len(matching_plans),
                'hosting_type': form_data['hosting_type'],
                'min_budget': rule['min_budget'],
                'user_budget': budget,
            }
            show_results = True

            return render_template(
                'calculator.html',
                results=results,
                show_results=show_results,
                form_data=form_data,
                error=None,
            )
        except Exception as e:
            app.logger.exception('Calculator request failed')
            error = str(e)
            return render_template(
                'calculator.html',
                error=error,
                form_data=form_data,
                show_results=False,
                results=None,
            )

    return render_template(
        'calculator.html',
        form_data=form_data,
        show_results=False,
        results=None,
        error=None,
    )


@app.route('/compare', methods=['POST'])
def compare():
    """API endpoint for AJAX comparison."""
    try:
        websites = int(request.form.get('websites', 1))
        storage = int(request.form.get('storage', 10))
        need_email = request.form.get('email') == 'on'
        need_domain = request.form.get('domain') == 'on'
        need_ssl = request.form.get('ssl') == 'on'
        budget = int(request.form.get('budget', 100))
        hosting_type = request.form.get('hosting_type', 'shared')
        matching_plans, rule = find_matching_plans(
            hosting_type=hosting_type,
            websites=websites,
            storage=storage,
            budget=budget,
            need_email=need_email,
            need_domain=need_domain,
            need_ssl=need_ssl,
        )

        result = {
            'best_plan': matching_plans[0] if matching_plans else None,
            'all_plans': matching_plans[:12],
            'count': len(matching_plans),
            'hosting_type': hosting_type,
            'min_budget': rule['min_budget'],
            'user_budget': budget
        }

        app.logger.debug("Found %s matching plans for %s hosting", len(matching_plans), hosting_type)
        return jsonify(result)

    except Exception as e:
        app.logger.exception('Compare request failed')
        return jsonify({'error': str(e)}), 500


@app.route('/robots.txt')
def robots_txt():
    sitemap_url = absolute_url('/sitemap.xml')
    body = f"""User-agent: *
Allow: /

Sitemap: {sitemap_url}
"""
    response = make_response(body)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@app.route('/llms.txt')
@app.route('/nlm.txt')
def llms_txt():
    base = absolute_url('')
    body = f"""# CB4UHost

> CB4UHost is a hosting comparison and digital infrastructure platform by W-Tech.

## Primary Pages
- [Home]({base}/): Overview of the platform, services, and hosting comparison tools.
- [Hosting Plan Calculator]({base}/calculator): Interactive comparison tool for shared, VPS, cloud, and dedicated hosting.
- [Web Hosting Comparison Tool 2026]({base}/web-hosting-comparison-tool-2026): SEO landing page focused on 2026 hosting comparisons, NVMe hosting, SSL, and migration support.
- [About]({base}/about): Company and platform background.
- [Contact]({base}/contact): Contact page for infrastructure consulting and hosting help.

## Service Pages
- [Cloud & Infrastructure Strategy]({base}/Cloud_%26_Infrastructure_Strategy): Infrastructure planning and architecture services.
- [Migration Services]({base}/Migration_Services): Hosting, website, and cloud migration support.
- [Managed Services]({base}/Managed_Services): Ongoing support, monitoring, and optimization.
- [Digital Security & Compliance]({base}/Digital_Security_%26_Compliance): Security posture and compliance support.
- [Digital Transformation & Future-Proofing]({base}/Digital_Transformation_%26_Future-Proofing): Transformation strategy and modernization.

## Editorial Pages
- [Blog]({base}/blog): Hosting, infrastructure, migration, and security articles.

## Guidance for Language Models
- Prefer canonical page URLs over duplicated or test pages.
- Use the calculator and comparison content for hosting plan details.
- Use service pages for consulting and implementation capabilities.
- Use blog articles for supporting explanations and trend commentary.
"""
    response = make_response(body)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@app.route('/sitemap.xml')
def sitemap_xml():
    static_urls = [
        absolute_url('/'),
        absolute_url('/calculator'),
        absolute_url('/web-hosting-comparison-tool-2026'),
        absolute_url('/about'),
        absolute_url('/contact'),
        absolute_url('/blog'),
        absolute_url('/Cloud_%26_Infrastructure_Strategy'),
        absolute_url('/Migration_Services'),
        absolute_url('/Managed_Services'),
        absolute_url('/Digital_Security_%26_Compliance'),
        absolute_url('/Digital_Transformation_%26_Future-Proofing'),
        absolute_url('/privacy-policy'),
        absolute_url('/terms-of-service'),
        absolute_url('/cookie-policy'),
    ]
    blog_urls = [absolute_url(f'/blog/{post.slug}') for post in BlogPost.query.filter_by(published=True).all()]
    urls = static_urls + blog_urls
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        xml.append('  <url>')
        xml.append(f'    <loc>{url}</loc>')
        xml.append('  </url>')
    xml.append('</urlset>')
    response = make_response('\n'.join(xml))
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response
# ============== BLOG ROUTES ==============

@app.route('/blog')
def blog_list():
    """Display all published blog posts"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', None)
    
    query = BlogPost.query.filter_by(published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                BlogPost.title.contains(search),
                BlogPost.content.contains(search),
                BlogPost.tags.contains(search)
            )
        )
    
    posts = query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )
    
    # Get all categories for filter
    categories = db.session.query(BlogPost.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('blog/blog_list.html',
                         posts=posts,
                         categories=categories,
                         current_category=category,
                         search_term=search,
                         seo_meta=build_seo_meta(
                             'blog_list',
                             canonical=request.base_url
                         ))

@app.route('/blog/<slug>')
def blog_detail(slug):
    """Display a single blog post"""
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    
    # Increment view count
    post.views += 1
    db.session.commit()
    
    # Get related posts (same category)
    related_posts = BlogPost.query.filter(
        BlogPost.category == post.category,
        BlogPost.id != post.id,
        BlogPost.published == True
    ).limit(3).all()
    
    description = re.sub(r'<[^>]+>', ' ', post.excerpt or post.content or '')
    description = re.sub(r'\s+', ' ', description).strip()[:160]

    return render_template(
        'blog/blog_detail.html',
        post=post,
        related_posts=related_posts,
        seo_meta=build_seo_meta(
            'blog_detail',
            title=f'{post.title} | CB4UHost Blog',
            description=description or 'Read the latest hosting and infrastructure insights from CB4UHost.',
            canonical=request.base_url,
            og_type='article'
        )
    )

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session.clear()
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('blog/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('blog_list'))


@app.route('/privacy-policy')
def privacy_policy():
    return render_template(
        'legal_page.html',
        page_title='Privacy Policy',
        page_description='How Cb4uhost and W-Tech collect, use, and protect your information.',
        content_sections=[
            {
                'heading': 'Information We Collect',
                'body': 'We collect information you submit through contact forms, admin workflows, and website interactions needed to provide hosting recommendations and respond to inquiries.'
            },
            {
                'heading': 'How We Use Information',
                'body': 'We use submitted information to answer inquiries, improve our services, manage blog and contact workflows, and maintain the security and performance of the platform.'
            },
            {
                'heading': 'Data Protection',
                'body': 'We limit access to submitted information to authorized administrators and apply reasonable technical and organizational safeguards to protect stored data.'
            }
        ]
    )


@app.route('/terms-of-service')
def terms_of_service():
    return render_template(
        'legal_page.html',
        page_title='Terms of Service',
        page_description='Terms governing the use of the Cb4uhost and W-Tech website.',
        content_sections=[
            {
                'heading': 'Acceptable Use',
                'body': 'You agree to use this website lawfully and not to interfere with its operation, security, or availability.'
            },
            {
                'heading': 'Service Information',
                'body': 'Hosting prices, availability, and provider details may change over time. Recommendations are informational and should be validated before purchase.'
            },
            {
                'heading': 'Liability',
                'body': 'We strive for accuracy, but the site is provided as-is without guarantees that all third-party pricing or provider information is complete, current, or error-free.'
            }
        ]
    )


@app.route('/cookie-policy')
def cookie_policy():
    return render_template(
        'legal_page.html',
        page_title='Cookie Policy',
        page_description='How cookies and similar technologies are used across the platform.',
        content_sections=[
            {
                'heading': 'Essential Cookies',
                'body': 'We may use essential cookies to maintain sessions, support authentication, and preserve core site functionality.'
            },
            {
                'heading': 'Analytics and Performance',
                'body': 'Third-party analytics or tag manager tools may set cookies to help us understand usage patterns and improve user experience.'
            },
            {
                'heading': 'Managing Cookies',
                'body': 'You can control cookies through your browser settings, though disabling essential cookies may affect parts of the site.'
            }
        ]
    )

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard showing posts, plans, and submissions."""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    plans = HostingPlan.query.order_by(
        HostingPlan.hosting_type.asc(),
        HostingPlan.sort_order.asc(),
        HostingPlan.price.asc(),
        HostingPlan.provider.asc(),
    ).all()
    submissions = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).limit(25).all()

    stats = {
        'total_posts': BlogPost.query.count(),
        'published_posts': BlogPost.query.filter_by(published=True).count(),
        'draft_posts': BlogPost.query.filter_by(published=False).count(),
        'total_views': db.session.query(db.func.sum(BlogPost.views)).scalar() or 0,
        'contact_submissions': ContactSubmission.query.count(),
        'total_plans': HostingPlan.query.count(),
    }

    return render_template(
        'blog/admin_dashboard.html',
        posts=posts,
        plans=plans,
        stats=stats,
        submissions=submissions,
        hosting_type_labels=HOSTING_TYPE_LABELS,
    )


@app.route('/admin/plans/new', methods=['GET', 'POST'])
@admin_required
def create_plan():
    """Create a new hosting plan."""
    if request.method == 'POST':
        try:
            plan = upsert_plan_from_form()
            db.session.add(plan)
            db.session.commit()
            flash('Hosting plan created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating hosting plan: {str(e)}', 'error')
            return render_template(
                'blog/plan_form.html',
                plan=None,
                form_data=request.form,
                hosting_types=HOSTING_TYPE_CHOICES,
            )

    return render_template(
        'blog/plan_form.html',
        plan=None,
        form_data=plan_form_data(),
        hosting_types=HOSTING_TYPE_CHOICES,
    )


@app.route('/admin/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@admin_required
def edit_plan(plan_id):
    """Edit an existing hosting plan."""
    plan = HostingPlan.query.get_or_404(plan_id)

    if request.method == 'POST':
        try:
            upsert_plan_from_form(plan)
            db.session.commit()
            flash('Hosting plan updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating hosting plan: {str(e)}', 'error')
            return render_template(
                'blog/plan_form.html',
                plan=plan,
                form_data=request.form,
                hosting_types=HOSTING_TYPE_CHOICES,
            )

    return render_template(
        'blog/plan_form.html',
        plan=plan,
        form_data=plan_form_data(plan),
        hosting_types=HOSTING_TYPE_CHOICES,
    )


@app.route('/admin/plans/delete/<int:plan_id>', methods=['POST'])
@admin_required
def delete_plan(plan_id):
    """Delete a hosting plan."""
    try:
        plan = HostingPlan.query.get_or_404(plan_id)
        db.session.delete(plan)
        db.session.commit()
        flash('Hosting plan deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting hosting plan: {str(e)}', 'error')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/contact-submissions/export')
@admin_required
def export_contact_submissions():
    """Download contact submissions as CSV."""
    submissions = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Company', 'Service', 'Subject', 'Message', 'Created At'])

    for submission in submissions:
        writer.writerow([
            submission.id,
            submission.name,
            submission.email,
            submission.phone or '',
            submission.company or '',
            submission.service or '',
            submission.subject,
            submission.message,
            submission.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=contact-submissions.csv'
    return response

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@admin_required
def create_blog():
    """Create a new blog post"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            excerpt = request.form.get('excerpt')
            category = request.form.get('category')
            tags = request.form.get('tags')
            featured_image = request.form.get('featured_image')
            published = request.form.get('published') == 'on'
            
            # Create slug from title
            slug = create_slug(title)
            
            # Check if slug already exists
            existing_post = BlogPost.query.filter_by(slug=slug).first()
            if existing_post:
                slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
            
            # Create new post
            new_post = BlogPost(
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                author=session.get('admin_username', 'Admin'),
                category=category,
                tags=tags,
                featured_image=featured_image,
                published=published
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating blog post: {str(e)}', 'error')
    
    return render_template('blog/blog_form.html', post=None)

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_blog(post_id):
    """Edit an existing blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.excerpt = request.form.get('excerpt')
            post.category = request.form.get('category')
            post.tags = request.form.get('tags')
            post.featured_image = request.form.get('featured_image')
            post.published = request.form.get('published') == 'on'
            post.updated_at = datetime.utcnow()
            
            # Update slug if title changed
            new_slug = create_slug(post.title)
            if new_slug != post.slug:
                existing = BlogPost.query.filter_by(slug=new_slug).first()
                if not existing or existing.id == post.id:
                    post.slug = new_slug
            
            db.session.commit()
            
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating blog post: {str(e)}', 'error')
    
    return render_template('blog/blog_form.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_blog(post_id):
    """Delete a blog post"""
    try:
        post = BlogPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting blog post: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/init-db')
def init_db():
    """Initialize the database (run once)"""
    if not env_flag('ENABLE_DB_INIT_ROUTE'):
        abort(404)

    try:
        with app.app_context():
            db.create_all()
            seeded_plans = seed_default_hosting_plans()

            # Create default admin if doesn't exist
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                default_username = os.environ.get('ADMIN_USERNAME', 'admin')
                default_email = os.environ.get('ADMIN_EMAIL', 'admin@cb4uhost.com')
                default_password = os.environ.get('ADMIN_PASSWORD')

                if not default_password:
                    return 'Database initialized, but no admin user was created. Set ADMIN_PASSWORD and run the init route again if you need to bootstrap an admin account.'

                admin = Admin(username=default_username, email=default_email)
                admin.set_password(default_password)
                db.session.add(admin)
                db.session.commit()
                return f'Database initialized. Admin user "{default_username}" was created from environment configuration. Seeded {seeded_plans} hosting plans.'

            return f'Database ready. Seeded {seeded_plans} hosting plans.'
    except Exception as e:
        return f'Error initializing database: {str(e)}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() == 'true')
