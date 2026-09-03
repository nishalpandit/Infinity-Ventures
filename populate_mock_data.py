import os
import django

# Set up Django environment if this script is run standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from myapp.models import CustomUser, VendorProfile, USERProfile, QuickService, Job, Bid, Subscription

# Clear existing mock data if any
CustomUser.objects.exclude(is_superuser=True).delete()

# Create USERs (User model)
USERs = []
for i in range(1, 6):
    user = CustomUser.objects.create_user(f'USER{i}', f'USER{i}@example.com', 'password123', role='USER')
    USERProfile.objects.create(user=user, phone_number=f"555-010{i}")
    USERs.append(user)

# Create Vendors
vendors_data = [
    {'username': 'techcorp', 'email': 'tech@example.com', 'company': 'TechCorp Solutions', 'category': 'IT Services', 'location': 'New York', 'rating': 4.8},
    {'username': 'johndoe', 'email': 'john@example.com', 'company': 'John Doe Freelance', 'category': 'Web Dev', 'location': 'London', 'rating': 4.5},
    {'username': 'marketingpro', 'email': 'marketing@example.com', 'company': 'Marketing Pro', 'category': 'Marketing', 'location': 'San Francisco', 'rating': 4.2},
    {'username': 'janesmith', 'email': 'jane@example.com', 'company': 'Jane Smith Design', 'category': 'Design', 'location': 'Berlin', 'rating': 4.9},
    {'username': 'dataanalytics', 'email': 'data@example.com', 'company': 'Data Analytics Inc', 'category': 'Data', 'location': 'Austin', 'rating': 4.7},
]

vendors = {}
for v_data in vendors_data:
    user = CustomUser.objects.create_user(v_data['username'], v_data['email'], 'password123', role='VENDOR')
    VendorProfile.objects.create(
        user=user,
        company_name=v_data['company'],
        category=v_data['category'],
        location=v_data['location'],
        rating=v_data['rating']
    )
    vendors[v_data['company']] = user

# Create Quick Services
qs_data = [
    {'title': 'Website Fix', 'USER': USERs[0], 'budget': 150.00, 'status': 'active'},
    {'title': 'Logo Design', 'USER': USERs[1], 'budget': 200.00, 'status': 'in-progress'},
    {'title': 'SEO Audit', 'USER': USERs[2], 'budget': 100.00, 'status': 'completed'},
    {'title': 'Server Setup', 'USER': USERs[3], 'budget': 350.00, 'status': 'active'},
    {'title': 'Bug Fixing', 'USER': USERs[4], 'budget': 500.00, 'status': 'cancelled'},
]

for qs in qs_data:
    QuickService.objects.create(
        title=qs['title'],
        USER=qs['USER'],
        budget=qs['budget'],
        status=qs['status']
    )

# Create Jobs
jobs_data = [
    {'title': 'Full Stack E-commerce App', 'USER': USERs[0], 'budget': 5000.00, 'bids': 5, 'status': 'active'},
    {'title': 'Mobile App Development', 'USER': USERs[1], 'budget': 8000.00, 'bids': 3, 'status': 'in-progress'},
    {'title': 'Brand Identity', 'USER': USERs[2], 'budget': 1500.00, 'bids': 10, 'status': 'completed'},
    {'title': 'Database Migration', 'USER': USERs[3], 'budget': 3000.00, 'bids': 2, 'status': 'active'},
]

jobs = {}
for j in jobs_data:
    job = Job.objects.create(
        title=j['title'],
        USER=j['USER'],
        budget=j['budget'],
        bids_count=j['bids'],
        status=j['status']
    )
    jobs[j['title']] = job

# Create Bids
bids_data = [
    {'vendor': 'TechCorp Solutions', 'job': 'Full Stack E-commerce App', 'amount': 4800.00, 'status': 'submitted'},
    {'vendor': 'John Doe Freelance', 'job': 'Full Stack E-commerce App', 'amount': 4500.00, 'status': 'selected'},
    {'vendor': 'Marketing Pro', 'job': 'Brand Identity', 'amount': 1200.00, 'status': 'rejected'},
    {'vendor': 'Data Analytics Inc', 'job': 'Database Migration', 'amount': 2900.00, 'status': 'submitted'},
]

for b in bids_data:
    Bid.objects.create(
        vendor=vendors[b['vendor']],
        job=jobs[b['job']],
        amount=b['amount'],
        status=b['status']
    )

# Create Subscriptions
subs_data = [
    {'vendor': 'TechCorp Solutions', 'pkg': 'Premium', 'amount': 199.99, 'status': 'success'},
    {'vendor': 'John Doe Freelance', 'pkg': 'Basic', 'amount': 49.99, 'status': 'success'},
    {'vendor': 'Marketing Pro', 'pkg': 'Standard', 'amount': 99.99, 'status': 'failed'},
    {'vendor': 'Jane Smith Design', 'pkg': 'Basic', 'amount': 49.99, 'status': 'success'},
    {'vendor': 'Data Analytics Inc', 'pkg': 'Premium', 'amount': 199.99, 'status': 'pending'},
]

for s in subs_data:
    Subscription.objects.create(
        vendor=vendors[s['vendor']],
        package_name=s['pkg'],
        amount=s['amount'],
        status=s['status']
    )

print("Mock data created successfully!")
