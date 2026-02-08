from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

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
        'Single': 'https://www.hostinger.in/web-hosting',
        'Premium': 'https://www.hostinger.in/web-hosting'
    },
    'bluehost': {
        'Shared': 'https://www.bluehost.in/hosting/shared'
    }
}

vps_buy_links = {
    'hostinger': {
        'KVM 2': 'https://www.hostinger.in/vps-hosting'
    },
    'bluehost': {
        'Enhanced NVMe 8': 'https://www.bluehost.in/hosting/vps'
    }
}

dedicated_buy_links = {
    'bigrock': {
        'Mach-1 SSD': 'https://www.bigrock.in/dedicated-server-hosting',
        'Mach-2 SSD': 'https://www.bigrock.in/dedicated-server-hosting',
        'Mach-3 SSD': 'https://www.bigrock.in/dedicated-server-hosting'
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
# ADD THESE IMPORTS

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

# Initialize Flask app FIRST
app = Flask(__name__)

# CRITICAL: Add secret key for sessions
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database AFTER app
db = SQLAlchemy(app)

# BLOG MODELS
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

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return render_template('home.html')

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')

@app.route('/service1')
def service1():

    return render_template('service1.html')

@app.route('/service2')
def service2():
    return render_template('service2.html')

@app.route('/service3')
def service3():
    return render_template('service3.html')

@app.route('/service4')
def service4():
    return render_template('service4.html')

@app.route('/service5')
def service5():
    return render_template('service5.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Us page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        flash('Thank you for contacting us! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

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
    """Main calculator page - FIXED for best match"""
    # Default form values
    form_data = {
        'websites': 1,
        'storage': 10,
        'budget': 200,
        'email': False,
        'domain': False,
        'ssl': False,
        'custom_plan': False,
        'hosting_type': 'shared',
        'cpu_cores': 2,  # ADD THIS
        'ram': 4         # ADD THIS
    }
    
    # Initialize these for all requests
    show_results = False
    results = None
    error = None
    
    if request.method == 'POST':
        try:
            print("Form data received:", request.form)
            
            # Parse values
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
            
            # Update form_data
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
            
            print(f"Processed form_data: {form_data}")
            
            # FIXED: Better budget multipliers and minimum budgets
            if form_data['hosting_type'] == 'vps':
                data_source = vps_data
                links_source = vps_buy_links
                min_budget = 500
                budget_multiplier = 3.0
            elif form_data['hosting_type'] == 'dedicated':
                data_source = dedicated_data
                links_source = dedicated_buy_links
                min_budget = 7000
                budget_multiplier = 3.0
            elif form_data['hosting_type'] == 'cloud':
                data_source = cloud_hosting_data
                links_source = cloud_hosting_buy_links
                min_budget = 200
                budget_multiplier = 3.0
            else:  # shared
                data_source = hosting_data
                links_source = buy_links
                min_budget = 50
                budget_multiplier = 3.0
            
            # Find matching plans
            matching_plans = []
            
            print(f"Searching in {len(data_source)} providers for {form_data['hosting_type']} hosting")
            
            for provider, plans in data_source.items():
                for plan_name, plan in plans.items():
                    meets_requirements = False
                    
                    # FIXED: More lenient matching criteria
                    if form_data['hosting_type'] in ['vps', 'dedicated', 'cloud']:
                        # For VPS, Dedicated, and Cloud
                        storage_ok = (
                            plan['storage_value'] == float('inf') or 
                            plan['storage_value'] >= storage * 0.5
                        )
                        
                        price_ok = plan['price'] <= budget * budget_multiplier
                        
                        # For cloud, check websites if specified
                        if form_data['hosting_type'] == 'cloud' and 'websites' in plan:
                            if plan['websites'] != "Unlimited":
                                websites_ok = plan['websites'] >= websites
                            else:
                                websites_ok = True
                            meets_requirements = price_ok and storage_ok and websites_ok
                        else:
                            meets_requirements = price_ok and storage_ok
                            
                    else:  # shared hosting
                        websites_ok = (
                            plan['websites'] == "Unlimited" or 
                            plan['websites'] >= websites
                        )
                        storage_ok = (
                            plan['storage_value'] == float('inf') or 
                            plan['storage_value'] >= storage * 0.5
                        )
                        price_ok = plan['price'] <= budget * budget_multiplier
                        
                        meets_requirements = price_ok and websites_ok and storage_ok
                    
                    if meets_requirements:
                        # Add buy link to the plan data
                        plan_with_link = plan.copy()
                        plan_with_link['buy_link'] = links_source.get(provider, {}).get(plan_name, '#')
                        
                        # Calculate score
                        plan_score = calculate_score(
                            plan, budget, websites, storage,
                            form_data['email'], form_data['domain'], form_data['ssl']
                        )
                        
                        print(f"Plan {provider} - {plan_name}: Score = {plan_score:.2f}, Price = ₹{plan['price']}")
                        
                        matching_plans.append({
                            'provider': provider,
                            'plan_name': plan_name,
                            'plan': plan_with_link,
                            'score': plan_score
                        })
            
            # Sort plans by score (higher is better)
            matching_plans.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"Found {len(matching_plans)} matching {form_data['hosting_type']} plans")
            if matching_plans:
                print(f"Best plan: {matching_plans[0]['provider']} - {matching_plans[0]['plan_name']} (Score: {matching_plans[0]['score']:.2f}, Price: ₹{matching_plans[0]['plan']['price']})")
            else:
                print("No matching plans found!")
            
            # FIXED: Organize results with proper structure for template
            if matching_plans:
                results = {
                    'best_plan': {
                        'provider': matching_plans[0]['provider'],
                        'plan_name': matching_plans[0]['plan_name'],
                        'plan': matching_plans[0]['plan']
                    },
                    'all_plans': [
                        {
                            'provider': p['provider'],
                            'plan_name': p['plan_name'],
                            'plan': p['plan']
                        }
                        for p in matching_plans[:12]
                    ],
                    'count': len(matching_plans),
                    'hosting_type': form_data['hosting_type'],
                    'min_budget': min_budget,
                    'user_budget': budget
                }
                show_results = True
            else:
                # No plans found
                results = {
                    'best_plan': None,
                    'all_plans': [],
                    'count': 0,
                    'hosting_type': form_data['hosting_type'],
                    'min_budget': min_budget,
                    'user_budget': budget
                }
                show_results = True
            
            print(f"Final results structure: count={results['count']}, has_best_plan={results['best_plan'] is not None}")
            
            # FIXED: Return with all required variables
            return render_template('calculator.html', 
                                 results=results, 
                                 show_results=show_results, 
                                 form_data=form_data,
                                 error=None)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error = str(e)
            print(f"ERROR: {error}")
            return render_template('calculator.html', 
                                 error=error, 
                                 form_data=form_data,
                                 show_results=False,
                                 results=None)
    
    # For GET requests - FIXED: Pass all required variables
    return render_template('calculator.html', 
                         form_data=form_data,
                         show_results=False,
                         results=None,
                         error=None)
@app.route('/compare', methods=['POST'])
def compare():
    """API endpoint for AJAX comparison - FIXED"""
    try:
        websites = int(request.form.get('websites', 1))
        storage = int(request.form.get('storage', 10))
        need_email = request.form.get('email') == 'on'
        need_domain = request.form.get('domain') == 'on'
        need_ssl = request.form.get('ssl') == 'on'
        budget = int(request.form.get('budget', 100))
        hosting_type = request.form.get('hosting_type', 'shared')
        
        print(f"Debug - Compare API: websites={websites}, storage={storage}, budget={budget}, type={hosting_type}")
        
        # Select data source
        if hosting_type == 'vps':
            data_source = vps_data
            min_budget = 500
            budget_multiplier = 3.0
        elif hosting_type == 'dedicated':
            data_source = dedicated_data
            min_budget = 7000
            budget_multiplier = 3.0
        elif hosting_type == 'cloud':
            data_source = cloud_hosting_data
            min_budget = 200
            budget_multiplier = 3.0
        else:
            data_source = hosting_data
            min_budget = 50
            budget_multiplier = 3.0
        
        # Find matching plans
        matching_plans = []
        
        for provider, plans in data_source.items():
            for plan_name, plan in plans.items():
                if hosting_type in ['vps', 'dedicated', 'cloud']:
                    storage_ok = (
                        plan['storage_value'] == float('inf') or 
                        plan['storage_value'] >= storage * 0.5
                    )
                    price_ok = plan['price'] <= budget * budget_multiplier
                    meets_requirements = price_ok and storage_ok
                else:
                    websites_ok = (
                        plan['websites'] == "Unlimited" or 
                        plan['websites'] >= websites
                    )
                    storage_ok = (
                        plan['storage_value'] == float('inf') or 
                        plan['storage_value'] >= storage * 0.5
                    )
                    price_ok = plan['price'] <= budget * budget_multiplier
                    meets_requirements = price_ok and websites_ok and storage_ok
                
                if meets_requirements:
                    plan_score = calculate_score(plan, budget, websites, storage, 
                                               need_email, need_domain, need_ssl)
                    matching_plans.append({
                        'provider': provider,
                        'plan_name': plan_name,
                        'plan': plan,
                        'score': plan_score
                    })
        
        matching_plans.sort(key=lambda x: x['score'], reverse=True)
        
        result = {
            'best_plan': matching_plans[0] if matching_plans else None,
            'all_plans': matching_plans[:12],
            'count': len(matching_plans),
            'hosting_type': hosting_type,
            'min_budget': min_budget,
            'user_budget': budget
        }
        
        print(f"Debug - Found {len(matching_plans)} plans")
        return jsonify(result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
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
                         search_term=search)

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
    
    return render_template('blog/blog_detail.html', post=post, related_posts=related_posts)

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
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('blog/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('blog_list'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard showing all posts"""
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    
    stats = {
        'total_posts': BlogPost.query.count(),
        'published_posts': BlogPost.query.filter_by(published=True).count(),
        'draft_posts': BlogPost.query.filter_by(published=False).count(),
        'total_views': db.session.query(db.func.sum(BlogPost.views)).scalar() or 0
    }
    
    return render_template('blog/admin_dashboard.html', posts=posts, stats=stats)

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
    try:
        with app.app_context():
            db.create_all()
            
            # Create default admin if doesn't exist
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin', email='admin@cb4uhost.com')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                return 'Database initialized! Default admin created (username: admin, password: admin123)'
            
            return 'Database already initialized!'
    except Exception as e:
        return f'Error initializing database: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)