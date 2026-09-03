import os
import django
import sys
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Job, Category, Location, CustomUser

def create_jobs():
    user = CustomUser.objects.filter(role='USER').first()
    if not user:
        print("No user found.")
        return
        
    category = Category.objects.filter(status='active').first()
    if not category:
        print("No active category found.")
        return
        
    location = Location.objects.filter(status='active').first()
    
    # Create Job 1
    job1 = Job.objects.create(
        user=user,
        title="Full Kitchen Renovation",
        category=category,
        description="Looking to remodel my entire kitchen including cabinets and flooring.",
        required_work=["Remove old cabinets", "Install new tile flooring", "Plumbing for new sink"],
        scope_of_work="Complete tear down and rebuild.",
        budget=150000.00,
        budget_type="Fixed budget",
        preferred_start_date=date(2026, 9, 1),
        expected_completion=date(2026, 10, 1),
        location=location,
        address="123 Example Street, Mumbai",
        pincode="400001",
        contact_name="Test User",
        contact_mobile="9876543210",
        status="open"
    )
    print(f"Created Job: {job1.title}")
    
    # Create Job 2
    job2 = Job.objects.create(
        user=user,
        title="Living Room Painting",
        category=category,
        description="Need the living room walls and ceiling painted.",
        required_work=["Wall prep", "2 coats of paint", "Ceiling painting"],
        scope_of_work="All walls and ceiling in the 20x15 living room.",
        budget=20000.00,
        budget_type="Budget range",
        preferred_start_date=date(2026, 8, 30),
        expected_completion=date(2026, 9, 5),
        location=location,
        address="456 Another St, Delhi",
        pincode="110001",
        contact_name="Test User",
        contact_mobile="9876543210",
        status="open"
    )
    print(f"Created Job: {job2.title}")

if __name__ == '__main__':
    create_jobs()
