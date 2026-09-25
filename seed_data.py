import os
import django
from decimal import Decimal
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from myapp.models import (
    VendorProfile, UserProfile, Category, Location,
    QuickService, Job, Bid, Subscription, Message
)

User = get_user_model()

def seed():
    print("Seeding database with comprehensive test data...")

    # 1. Locations
    locations_data = [
        ('Jharkhand', 'Ranchi'),
        ('Jharkhand', 'Jamshedpur'),
        ('Maharashtra', 'Mumbai'),
        ('Maharashtra', 'Pune'),
        ('Delhi', 'New Delhi'),
        ('Karnataka', 'Bengaluru'),
        ('West Bengal', 'Kolkata'),
        ('Tamil Nadu', 'Chennai'),
        ('Telangana', 'Hyderabad'),
    ]
    locations = {}
    for state, city in locations_data:
        loc, _ = Location.objects.get_or_create(state=state, city=city, defaults={'status': 'active'})
        loc.status = 'active'
        loc.save()
        locations[f"{city}, {state}"] = loc

    ranchi_loc = locations.get('Ranchi, Jharkhand')
    mumbai_loc = locations.get('Mumbai, Maharashtra')

    # 2. Categories
    categories_data = [
        ('Plumbing', 'both'),
        ('Electrical', 'both'),
        ('AC Repair', 'quick_service'),
        ('Carpentry', 'both'),
        ('Painting', 'job'),
        ('Cleaning', 'quick_service'),
        ('Full Renovation', 'job'),
        ('Waterproofing', 'job'),
        ('Appliance Repair', 'quick_service'),
    ]
    categories = {}
    for name, stype in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'service_type': stype, 'status': 'active'})
        cat.service_type = stype
        cat.status = 'active'
        cat.save()
        categories[name] = cat

    # 3. Superuser / Admin
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@sugguservices.com', 'first_name': 'Super', 'last_name': 'Admin', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True})
    admin_user.set_password('admin123')
    admin_user.role = 'ADMIN'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    UserProfile.objects.get_or_create(user=admin_user, defaults={'phone_number': '+91 98765 43210'})

    # 4. Customers (Users)
    customer_data = [
        ('ananya', 'ananya@example.com', 'Ananya', 'Sharma', '+91 98123 45678', 'pass123'),
        ('rahul', 'rahul@example.com', 'Rahul', 'Verma', '+91 98234 56789', 'pass123'),
        ('priya', 'priya@example.com', 'Priya', 'Singh', '+91 98345 67890', 'pass123'),
    ]
    customers = {}
    for username, email, fname, lname, phone, pwd in customer_data:
        u, _ = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': fname, 'last_name': lname, 'role': 'USER'})
        u.set_password(pwd)
        u.first_name = fname
        u.last_name = lname
        u.email = email
        u.role = 'USER'
        u.save()
        UserProfile.objects.update_or_create(user=u, defaults={'phone_number': phone})
        customers[username] = u

    ananya = customers['ananya']
    rahul = customers['rahul']

    # 5. Vendors
    vendor_data = [
        ('technician_ravi', 'ravi@quickfix.com', 'Ravi', 'Kumar', '+91 98901 12345', 'pass123', 'QuickFix Services', 'Plumbing', 'Ranchi, Jharkhand', 'vendor', 4.8, 8),
        ('spark_india', 'spark@sparkindia.in', 'Vikram', 'Aditya', '+91 98902 23456', 'pass123', 'Spark India Electricals', 'Electrical', 'Ranchi, Jharkhand', 'company', 4.9, 12),
        ('buildright', 'contact@buildright.com', 'Amit', 'Patel', '+91 98903 34567', 'pass123', 'BuildRight Contractors', 'Full Renovation', 'Ranchi, Jharkhand', 'company', 4.7, 15),
        ('cleanpro', 'info@cleanpro.com', 'Sunil', 'Mehta', '+91 98904 45678', 'pass123', 'CleanPro Facility Management', 'Cleaning', 'Mumbai, Maharashtra', 'vendor', 4.6, 5),
    ]
    vendors = {}
    for uname, email, fname, lname, phone, pwd, comp_name, cat_name, loc_str, v_type, rating, exp in vendor_data:
        u, _ = User.objects.get_or_create(username=uname, defaults={'email': email, 'first_name': fname, 'last_name': lname, 'role': 'VENDOR'})
        u.set_password(pwd)
        u.role = 'VENDOR'
        u.first_name = fname
        u.last_name = lname
        u.email = email
        u.save()
        UserProfile.objects.update_or_create(user=u, defaults={'phone_number': phone})
        VendorProfile.objects.update_or_create(
            user=u,
            defaults={
                'company_name': comp_name,
                'category': cat_name,
                'location': loc_str,
                'vendor_type': v_type,
                'rating': Decimal(str(rating)),
                'experience': exp,
                'about': f"Certified experts in {cat_name} with over {exp} years of industry experience.",
                'address': f"Plot {exp*10}, Main Industrial Area, {loc_str}"
            }
        )
        vendors[uname] = u

    ravi = vendors['technician_ravi']
    spark = vendors['spark_india']
    buildright = vendors['buildright']
    cleanpro = vendors['cleanpro']

    # 6. Quick Services for Ananya
    qs_samples = [
        {
            'title': 'Kitchen sink pipe leakage & drainage fix',
            'category': categories['Plumbing'],
            'description': 'Main kitchen sink drain pipe is leaking continuously under the cabinet. Requires urgent PVC pipe replacement and sealing.',
            'required_work': ['Pipe Replacement', 'Sealant Application', 'Drain Trap Cleaning'],
            'budget': Decimal('950.00'),
            'shift_availability': 'Morning (9 AM - 12 PM)',
            'preferred_date': date.today() + timedelta(days=1),
            'preferred_time': time(10, 30),
            'location': ranchi_loc,
            'address': 'Flat 402, Green Valley Apartments, Bariatu, Ranchi',
            'status': 'selected',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        },
        {
            'title': 'Split AC not cooling & unusual noise',
            'category': categories['AC Repair'],
            'description': '1.5 Ton Voltas Split AC blowing normal air instead of cooling. Needs refrigerant gas check and deep coil cleaning.',
            'required_work': ['Gas Check', 'Coil Cleaning', 'Filter Wash'],
            'budget': Decimal('1800.00'),
            'shift_availability': 'Afternoon (1 PM - 4 PM)',
            'preferred_date': date.today() + timedelta(days=2),
            'preferred_time': time(14, 0),
            'location': ranchi_loc,
            'address': 'B-12, Circular Road, Lalpur, Ranchi',
            'status': 'open',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        },
        {
            'title': 'Ceiling fan replacement and MCB tripping issue',
            'category': categories['Electrical'],
            'description': 'Master bedroom fan is jammed and tripping main MCB whenever turned on. Replacement fan is ready, need installation & wiring check.',
            'required_work': ['Fan Installation', 'MCB Inspection', 'Wiring Safety Check'],
            'budget': Decimal('750.00'),
            'shift_availability': 'Evening (5 PM - 8 PM)',
            'preferred_date': date.today() - timedelta(days=4),
            'preferred_time': time(17, 30),
            'location': ranchi_loc,
            'address': 'House 88, Kanke Road, Ranchi',
            'status': 'completed',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        },
        {
            'title': 'Sofa deep shampoo cleaning (3+2 seater)',
            'category': categories['Cleaning'],
            'description': 'Fabric sofa needs professional foam shampoo cleaning, dust extraction, and anti-bacterial spray treatment.',
            'required_work': ['Dry Vacuuming', 'Shampoo Extraction', 'Fabric Sanitization'],
            'budget': Decimal('2200.00'),
            'shift_availability': 'Flexible',
            'preferred_date': date.today() + timedelta(days=5),
            'preferred_time': time(11, 0),
            'location': ranchi_loc,
            'address': 'Flat 402, Green Valley Apartments, Bariatu, Ranchi',
            'status': 'open',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        }
    ]

    created_qs = []
    for q_data in qs_samples:
        qs, _ = QuickService.objects.get_or_create(
            title=q_data['title'],
            user=q_data['user'],
            defaults=q_data
        )
        for k, v in q_data.items():
            setattr(qs, k, v)
        qs.save()
        created_qs.append(qs)

    # 7. Jobs for Ananya
    job_samples = [
        {
            'title': 'Full 3BHK Apartment Interior Renovation',
            'category': categories['Full Renovation'],
            'description': 'Complete interior revamp of a 1450 sqft 3BHK flat including false ceiling with LED cob lights, modular kitchen cabinetry with quartz countertop, and master bedroom wooden wardrobe.',
            'required_work': ['False Ceiling (Gypsum)', 'Modular Kitchen', 'Wardrobe Carpentry', 'Wall Putty & Primer'],
            'scope_of_work': 'Procurement of marine plywood, hardware (Hettich/Hafele), false ceiling framing, electrical point shifts, and painting.',
            'materials_details': 'BWP grade 710 marine ply, 1mm merino laminates, Saint-Gobain gypsum boards.',
            'additional_requirements': 'All debris removal included. Work must be finished strictly within 45 days.',
            'budget': Decimal('480000.00'),
            'budget_type': 'Fixed Price',
            'preferred_start_date': date.today() + timedelta(days=7),
            'expected_completion': date.today() + timedelta(days=52),
            'required_time': '45 Days',
            'shift_availability': 'Full Day (9 AM - 6 PM)',
            'working_hours': '8 hours daily',
            'location': ranchi_loc,
            'address': 'Flat 402, Green Valley Apartments, Bariatu, Ranchi',
            'pincode': '834009',
            'status': 'selected',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        },
        {
            'title': 'Terrace Waterproofing and PU Coating (2200 sq.ft)',
            'category': categories['Waterproofing'],
            'description': 'Comprehensive rooftop waterproofing treatment to stop ceiling dampness. Crack filling with elastomeric compound, two coats of Dr. Fixit polymer modified mortar, followed by solar reflective heat-insulation PU top coat.',
            'required_work': ['Surface Grinding', 'Crack Filling', '2 Coats Fiber Mesh Waterproofing', 'Solar Topcoat'],
            'scope_of_work': 'Cleaning terrace thoroughly, treating expansion joints, coating parapet walls up to 1.5 ft.',
            'materials_details': 'Dr. Fixit Newcoat Ezee / Asian Paints SmartCare Damp Proof Ultra.',
            'additional_requirements': 'Minimum 5 years warranty with written service bond.',
            'budget': Decimal('95000.00'),
            'budget_type': 'Fixed Price',
            'preferred_start_date': date.today() + timedelta(days=10),
            'expected_completion': date.today() + timedelta(days=18),
            'required_time': '8 Days',
            'shift_availability': 'Morning to Evening',
            'working_hours': '9:00 AM - 5:00 PM',
            'location': ranchi_loc,
            'address': 'Plot 14, Morabadi Hills, Ranchi',
            'pincode': '834008',
            'status': 'open',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        },
        {
            'title': 'Commercial Office 3-Phase Rewiring & Distribution Box Upgrade',
            'category': categories['Electrical'],
            'description': 'Replace old aluminum conduits and rewiring with FR PVC insulated copper cables for 12 workstations, server rack UPS wiring, and Schneider MCCB panel board installation.',
            'required_work': ['Copper Wiring Pulling', 'Panel Board Replacement', 'Earthing Resistance Test'],
            'scope_of_work': 'Complete circuit segregation, label all breakers, provide load balance certificate.',
            'materials_details': 'Polycab/Finolex FR cables, Schneider Acti9 MCB/MCCB.',
            'additional_requirements': 'Work must be done during weekend to avoid disruption to office work.',
            'budget': Decimal('135000.00'),
            'budget_type': 'Fixed Price',
            'preferred_start_date': date.today() - timedelta(days=15),
            'expected_completion': date.today() - timedelta(days=1),
            'required_time': '2 Weekends',
            'shift_availability': 'Weekend Overnight',
            'working_hours': '10:00 AM - 8:00 PM',
            'location': ranchi_loc,
            'address': '3rd Floor, Tech Park, Lalpur, Ranchi',
            'pincode': '834001',
            'status': 'completed',
            'user': ananya,
            'contact_name': 'Ananya Sharma',
            'contact_mobile': '+91 98123 45678'
        }
    ]

    created_jobs = []
    for j_data in job_samples:
        job, _ = Job.objects.get_or_create(
            title=j_data['title'],
            user=j_data['user'],
            defaults=j_data
        )
        for k, v in j_data.items():
            setattr(job, k, v)
        job.save()
        created_jobs.append(job)

    # 8. Bids / Quotations
    # Bids on QS 1 (Sink Pipe Leakage)
    qs_sink = created_qs[0]
    Bid.objects.update_or_create(
        quick_service=qs_sink, vendor=ravi,
        defaults={
            'amount': Decimal('850.00'),
            'estimated_time': '2 Hours',
            'proposal': 'Can visit tomorrow morning at 10 AM. Will replace faulty coupling and install heavy-duty PVC pipe with silicone sealing.',
            'status': 'selected'
        }
    )
    Bid.objects.update_or_create(
        quick_service=qs_sink, vendor=spark,
        defaults={
            'amount': Decimal('1100.00'),
            'estimated_time': 'Same Day',
            'proposal': 'Complete plumbing inspection and replacement with branded Astral fittings.',
            'status': 'submitted'
        }
    )

    # Bids on QS 2 (AC Repair)
    qs_ac = created_qs[1]
    Bid.objects.update_or_create(
        quick_service=qs_ac, vendor=ravi,
        defaults={
            'amount': Decimal('1650.00'),
            'estimated_time': '3-4 Hours',
            'proposal': 'Will test with digital manifold gauge, fix minor flaring leaks, top up R32 gas and wash both indoor and outdoor units.',
            'status': 'submitted'
        }
    )
    Bid.objects.update_or_create(
        quick_service=qs_ac, vendor=cleanpro,
        defaults={
            'amount': Decimal('1900.00'),
            'estimated_time': '4 Hours',
            'proposal': 'Jet pump deep chemical foam coil cleaning + gas leak check included.',
            'status': 'submitted'
        }
    )

    # Bids on Job 1 (Interior Renovation)
    job_renov = created_jobs[0]
    Bid.objects.update_or_create(
        job=job_renov, vendor=buildright,
        defaults={
            'amount': Decimal('465000.00'),
            'estimated_time': '40 Days',
            'proposal': 'Turnkey execution with dedicated civil engineer on site. We provide 3D renders before carpentry, 10-year warranty on modular kitchen, and milestone-based payments.',
            'status': 'selected'
        }
    )
    Bid.objects.update_or_create(
        job=job_renov, vendor=spark,
        defaults={
            'amount': Decimal('495000.00'),
            'estimated_time': '45 Days',
            'proposal': 'Comprehensive interior fit-out. Premium hardware, branded finishes and certified electricians for smart lighting.',
            'status': 'submitted'
        }
    )

    # Bids on Job 2 (Waterproofing)
    job_water = created_jobs[1]
    Bid.objects.update_or_create(
        job=job_water, vendor=buildright,
        defaults={
            'amount': Decimal('89000.00'),
            'estimated_time': '7 Days',
            'proposal': '3-layer polymer elastomeric system with 300 GSM glass fiber mesh sandwich layer. 7 years unconditional guarantee against seepage.',
            'status': 'submitted'
        }
    )
    Bid.objects.update_or_create(
        job=job_water, vendor=cleanpro,
        defaults={
            'amount': Decimal('92000.00'),
            'estimated_time': '8 Days',
            'proposal': 'High pressure water jet cleaning + 2 coats polymer coating + UV resistant heat shield coating.',
            'status': 'submitted'
        }
    )

    # Update bids count
    for qs in created_qs:
        qs.bids_count = qs.bids.count()
        qs.save()
    for job in created_jobs:
        job.bids_count = job.bids.count()
        job.save()

    # 9. Messages between Ananya and Vendors
    # Chat with Ravi Kumar
    msg_flow_ravi = [
        (ananya, ravi, "Hello Ravi, I saw your quotation for the sink pipe repair. Are you available tomorrow morning?"),
        (ravi, ananya, "Hello Ananya! Yes, I can be at your place by 10:30 AM with all replacement pipes and seals."),
        (ananya, ravi, "Great, I have selected your quotation on the portal. Please remember to bring heavy duty PVC fittings."),
        (ravi, ananya, "Noted! I only carry Supreme and Astral high pressure fittings. See you tomorrow at 10:30 AM.")
    ]
    for sender, receiver, text in msg_flow_ravi:
        Message.objects.get_or_create(
            sender=sender, receiver=receiver, content=text,
            defaults={'quick_service': qs_sink, 'is_read': True}
        )

    # Chat with BuildRight Contractors
    msg_flow_build = [
        (buildright, ananya, "Hi Ananya, thank you for shortlisting BuildRight for your 3BHK renovation project!"),
        (ananya, buildright, "Hello Amit! We reviewed your proposal and liked your portfolio. When can we do a site measurement?"),
        (buildright, ananya, "Our architect can visit this Friday at 3:00 PM with laminate and material sample swatches."),
        (ananya, buildright, "Friday 3 PM works perfectly. I will inform building security.")
    ]
    for sender, receiver, text in msg_flow_build:
        Message.objects.get_or_create(
            sender=sender, receiver=receiver, content=text,
            defaults={'job': job_renov, 'is_read': True}
        )

    # 10. Subscriptions & Payments
    subscriptions_data = [
        (ravi, 'Professional Monthly', Decimal('2499.00'), 'success', timezone.now() - timedelta(days=25)),
        (spark, 'Enterprise Annual', Decimal('19999.00'), 'success', timezone.now() - timedelta(days=60)),
        (buildright, 'Enterprise Annual', Decimal('19999.00'), 'success', timezone.now() - timedelta(days=40)),
        (cleanpro, 'Starter 50 Bids', Decimal('999.00'), 'success', timezone.now() - timedelta(days=10)),
        (ravi, 'Bid Booster Pack', Decimal('499.00'), 'success', timezone.now() - timedelta(days=3)),
    ]
    for v_user, pkg_name, amt, st, dt in subscriptions_data:
        sub, _ = Subscription.objects.get_or_create(
            vendor=v_user, package_name=pkg_name, amount=amt, status=st,
            defaults={'created_at': dt}
        )
        sub.created_at = dt
        sub.save()

    print("Seeding completed successfully!")
    print(f"Users: {User.objects.count()}, Vendors: {VendorProfile.objects.count()}, QS: {QuickService.objects.count()}, Jobs: {Job.objects.count()}, Bids: {Bid.objects.count()}, Messages: {Message.objects.count()}")

if __name__ == '__main__':
    seed()
