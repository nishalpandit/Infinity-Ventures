import os
import django
import random
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import VendorProfile, QuickService, Job, Bid, Subscription

print("Clearing old data...")
VendorProfile.objects.all().delete()
QuickService.objects.all().delete()
Job.objects.all().delete()
Bid.objects.all().delete()
Subscription.objects.all().delete()

print("Creating Vendors...")
vendors = [
    VendorProfile.objects.create(name='Spark India', vendor_type='company', category='Electrical', location='Ranchi', rating=4.5),
    VendorProfile.objects.create(name='Ravi Kumar', vendor_type='outsider', category='Plumbing', location='Ranchi', rating=4.2),
    VendorProfile.objects.create(name='Om Sai Services', vendor_type='company', category='AC Repair', location='Bariatu', rating=4.8),
    VendorProfile.objects.create(name='BuildRight Contractors', vendor_type='company', category='Construction', location='Morabadi', rating=4.9),
    VendorProfile.objects.create(name='Neha Singh', vendor_type='outsider', category='Interior Design', location='Kanke', rating=4.0),
]

print("Creating Quick Services...")
QuickService.objects.create(title='AC cooling issue', USER_name='Ananya Sharma', budget=1500.00, status='in-progress', created_at=timezone.now() - timedelta(days=2))
QuickService.objects.create(title='Kitchen sink leakage', USER_name='Rahul Verma', budget=800.00, status='active', created_at=timezone.now() - timedelta(days=1))
QuickService.objects.create(title='Ceiling fan installation', USER_name='Sneha Patel', budget=600.00, status='completed', created_at=timezone.now() - timedelta(days=5))

print("Creating Jobs...")
Job.objects.create(title='Full House Renovation', USER_name='Amit Singh', budget=450000.00, bids_count=8, status='active', created_at=timezone.now() - timedelta(days=10))
Job.objects.create(title='Terrace waterproofing', USER_name='Priya Roy', budget=85000.00, bids_count=6, status='active', created_at=timezone.now() - timedelta(days=15))
Job.objects.create(title='Office electrical rewiring', USER_name='Vikas Gupta', budget=120000.00, bids_count=5, status='in-progress', created_at=timezone.now() - timedelta(days=30))

print("Creating Bids...")
Bid.objects.create(vendor_name='BuildRight Contractors', job_title='Full House Renovation', amount=440000.00, status='submitted', created_at=timezone.now() - timedelta(days=2))
Bid.objects.create(vendor_name='Om Sai Services', job_title='AC cooling issue', amount=1250.00, status='selected', created_at=timezone.now() - timedelta(hours=5))
Bid.objects.create(vendor_name='Spark India', job_title='Office electrical rewiring', amount=115000.00, status='selected', created_at=timezone.now() - timedelta(days=20))

print("Creating Subscriptions...")
Subscription.objects.create(vendor_name='BuildRight Contractors', package_name='Premium Plan', amount=4999.00, status='success', created_at=timezone.now() - timedelta(days=3))
Subscription.objects.create(vendor_name='Om Sai Services', package_name='Standard Plan', amount=1999.00, status='success', created_at=timezone.now() - timedelta(days=10))

print("Mock data created successfully!")
