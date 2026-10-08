import os
import django
import random
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myapp.models import QuickService, Category, CustomUser, VendorProfile

def seed_data():
    print("Seeding QuickServices for Ranchi (Namkom & Lalpur)...")

    # 1. Ensure a vendor exists
    vendor, created = CustomUser.objects.get_or_create(username='ranchi_vendor', defaults={
        'email': 'vendor@ranchi.com',
        'role': 'VENDOR'
    })
    if created:
        vendor.set_password('pass123')
        vendor.save()
        VendorProfile.objects.create(user=vendor, company_name='Ranchi QuickFix', mobile='9999999999')
        print("Created mock vendor 'ranchi_vendor'")

    # 2. Get some categories
    cats = list(Category.objects.all())
    if not cats:
        print("No categories found. Creating one...")
        cat = Category.objects.create(name='Appliances', is_active=True)
        cats.append(cat)

    # 3. Create services in Namkom
    # Namkom coords: Lat 23.3361, Lon 85.3853
    # Lalpur coords: Lat 23.3685, Lon 85.3286
    
    locations = [
        ("Namkom", 23.3361, 85.3853),
        ("Lalpur", 23.3685, 85.3286),
        ("Kanke", 23.4116, 85.3232)
    ]

    for loc_name, lat, lon in locations:
        for i in range(2):
            cat = random.choice(cats)
            title = f"Expert {cat.name} Service in {loc_name}"
            qs, created = QuickService.objects.get_or_create(
                title=title,
                vendor=vendor,
                defaults={
                    'category': cat,
                    'description': f"Best {cat.name} service provided by our top professionals in {loc_name}.",
                    'base_price': Decimal(random.randint(299, 1499)),
                    'locality': loc_name,
                    'latitude': lat,
                    'longitude': lon,
                    'service_radius_km': 15.0,
                    'status': 'active'
                }
            )
            if created:
                print(f"Created service: {qs.title} at {loc_name}")
            else:
                print(f"Service already exists: {qs.title}")

if __name__ == '__main__':
    seed_data()
    print("Done!")
