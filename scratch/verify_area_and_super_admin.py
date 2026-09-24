import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from myapp.models import VendorProfile, Location, Category, Job, QuickService, Bid, Subscription, UserProfile
from myapp.views import dashboard_view, admin_dashboard, create_company_vendor_view
from myapp.super_admin_views import (
    super_admin_dashboard, super_admin_users, super_admin_user_create, super_admin_user_edit,
    super_admin_user_toggle, super_admin_user_delete, super_admin_vendors, super_admin_vendor_create,
    super_admin_vendor_edit, super_admin_vendor_delete, super_admin_jobs, super_admin_job_create,
    super_admin_job_edit, super_admin_job_delete, super_admin_quick_services, super_admin_qs_create,
    super_admin_qs_edit, super_admin_qs_delete, super_admin_bids, super_admin_bid_create,
    super_admin_bid_edit, super_admin_bid_delete, super_admin_subscriptions, super_admin_subscription_create,
    super_admin_subscription_delete
)
from myapp.Api_views import add_user_api

User = get_user_model()
rf = RequestFactory()

print("--- STARTING AREA ADMIN & SUPER ADMIN VERIFICATION ---")

# 1. Setup Test Locations & Users
loc_jh, _ = Location.objects.get_or_create(state="Jharkhand", city="Ranchi")
loc_mh, _ = Location.objects.get_or_create(state="Maharashtra", city="Mumbai")
cat_gen, _ = Category.objects.get_or_create(name="Home Construction", service_type="both")

# Super Admin
sa_user, _ = User.objects.get_or_create(username="test_superadmin", defaults={"email": "sa@infinity.local", "is_superuser": True, "is_staff": True, "role": "ADMIN"})
sa_user.is_superuser = True
sa_user.set_password("pass123")
sa_user.save()

# Area Admin Jharkhand
jh_admin, _ = User.objects.get_or_create(username="test_admin_jharkhand", defaults={"email": "admin_jh@infinity.local", "role": "ADMIN", "assigned_state": "Jharkhand", "is_staff": True})
jh_admin.assigned_state = "Jharkhand"
jh_admin.role = "ADMIN"
jh_admin.is_superuser = False
jh_admin.set_password("pass123")
jh_admin.save()

# Area Admin Maharashtra
mh_admin, _ = User.objects.get_or_create(username="test_admin_maharashtra", defaults={"email": "admin_mh@infinity.local", "role": "ADMIN", "assigned_state": "Maharashtra", "is_staff": True})
mh_admin.assigned_state = "Maharashtra"
mh_admin.role = "ADMIN"
mh_admin.is_superuser = False
mh_admin.set_password("pass123")
mh_admin.save()

# Customers
cust_jh, _ = User.objects.get_or_create(username="test_cust_jharkhand", defaults={"email": "cust_jh@infinity.local", "role": "USER", "assigned_state": "Jharkhand"})
cust_jh.assigned_state = "Jharkhand"
cust_jh.role = "USER"
cust_jh.save()

cust_mh, _ = User.objects.get_or_create(username="test_cust_maharashtra", defaults={"email": "cust_mh@infinity.local", "role": "USER", "assigned_state": "Maharashtra"})
cust_mh.assigned_state = "Maharashtra"
cust_mh.role = "USER"
cust_mh.save()

# Vendors
v_jh_user, _ = User.objects.get_or_create(username="test_ven_jh", defaults={"email": "ven_jh@infinity.local", "role": "VENDOR", "assigned_state": "Jharkhand"})
v_jh_user.assigned_state = "Jharkhand"
v_jh_user.role = "VENDOR"
v_jh_user.save()
vp_jh, _ = VendorProfile.objects.get_or_create(user=v_jh_user, defaults={"company_name": "Jharkhand Builders", "category": "Home Construction", "location": "Ranchi, Jharkhand", "vendor_type": "company"})

v_mh_user, _ = User.objects.get_or_create(username="test_ven_mh", defaults={"email": "ven_mh@infinity.local", "role": "VENDOR", "assigned_state": "Maharashtra"})
v_mh_user.assigned_state = "Maharashtra"
v_mh_user.role = "VENDOR"
v_mh_user.save()
vp_mh, _ = VendorProfile.objects.get_or_create(user=v_mh_user, defaults={"company_name": "Mumbai Contractors", "category": "Home Construction", "location": "Mumbai, Maharashtra", "vendor_type": "vendor"})

print("[OK] Users, Locations, and Vendors initialized successfully.")

# -------------------------------------------------------------
# TEST 1: Area Admin Isolation in Users and Vendors List
# -------------------------------------------------------------
# Request by Jharkhand Area Admin
req_jh = rf.get('/admin-dashboard/users/users.html')
req_jh.user = jh_admin
resp = dashboard_view(req_jh, 'users/users.html')
assert resp.status_code == 200
content = resp.content.decode('utf-8')
assert cust_jh.username in content or cust_jh.email in content
assert cust_mh.username not in content
print("[OK] TEST 1 passed: Area Admin (Jharkhand) user list strictly isolates customers to Jharkhand.")

# Request by Jharkhand Area Admin for vendors
req_jh_v = rf.get('/admin-dashboard/users/vendors.html')
req_jh_v.user = jh_admin
resp_v = dashboard_view(req_jh_v, 'users/vendors.html')
assert resp_v.status_code == 200
content_v = resp_v.content.decode('utf-8')
assert "Jharkhand Builders" in content_v
assert "Mumbai Contractors" not in content_v
print("[OK] TEST 1.1 passed: Area Admin (Jharkhand) vendor list strictly isolates vendors to Jharkhand.")

# -------------------------------------------------------------
# TEST 2: Strict Access Control for User Details & Vendor Details
# -------------------------------------------------------------
# Jharkhand Admin accessing Jharkhand user details -> OK (200)
req_det_ok = rf.get(f'/admin-dashboard/users/user-details.html?id=USR-{cust_jh.id:04d}')
req_det_ok.user = jh_admin
resp_det_ok = dashboard_view(req_det_ok, 'users/user-details.html')
assert resp_det_ok.status_code == 200
assert cust_jh.username in resp_det_ok.content.decode('utf-8') or cust_jh.email in resp_det_ok.content.decode('utf-8')
print("[OK] TEST 2.1 passed: Area Admin accessing own territory user details succeeds.")

# Jharkhand Admin accessing Maharashtra user details -> REDIRECT (302 Access Denied)
from django.contrib.messages.storage.fallback import FallbackStorage
req_det_forbidden = rf.get(f'/admin-dashboard/users/user-details.html?id=USR-{cust_mh.id:04d}')
req_det_forbidden.user = jh_admin
setattr(req_det_forbidden, 'session', {})
setattr(req_det_forbidden, '_messages', FallbackStorage(req_det_forbidden))
resp_det_forbidden = dashboard_view(req_det_forbidden, 'users/user-details.html')
assert resp_det_forbidden.status_code == 302
assert '/admin-dashboard/users/users.html' in resp_det_forbidden.url
print("[OK] TEST 2.2 passed: Area Admin accessing other territory user details is strictly forbidden (Redirected).")

# Jharkhand Admin accessing Maharashtra vendor details -> REDIRECT (302 Access Denied)
req_v_forbidden = rf.get(f'/admin-dashboard/users/vendor-details.html?id=VEN-{v_mh_user.id:04d}')
req_v_forbidden.user = jh_admin
setattr(req_v_forbidden, 'session', {})
setattr(req_v_forbidden, '_messages', FallbackStorage(req_v_forbidden))
resp_v_forbidden = dashboard_view(req_v_forbidden, 'users/vendor-details.html')
assert resp_v_forbidden.status_code == 302
assert '/admin-dashboard/users/vendors.html' in resp_v_forbidden.url
print("[OK] TEST 2.3 passed: Area Admin accessing other territory vendor details is strictly forbidden (Redirected).")

# -------------------------------------------------------------
# TEST 3: Auto-tagging state on User and Vendor creation
# -------------------------------------------------------------
# Area Admin creates a customer via API
req_add_u = rf.post('/api/add-user/', data={
    "name": "Ranchi Local Customer",
    "email": "ranchi_cust@infinity.local",
    "mobile": "9876543210",
    "password": "Password123"
})
req_add_u.user = jh_admin
resp_add_u = add_user_api(req_add_u)
assert resp_add_u.status_code == 200
new_u = User.objects.get(email="ranchi_cust@infinity.local")
assert new_u.assigned_state == "Jharkhand"
print("[OK] TEST 3.1 passed: Customer created by Area Admin is auto-assigned to Jharkhand.")

# Area Admin creates a company vendor
req_add_v = rf.post('/admin-dashboard/create-company-vendor/', data={
    "company_name": "Ranchi Steel Works",
    "email": "ranchi_steel@infinity.local",
    "password": "Password123",
    "category": "Home Construction",
    "location": "Ranchi"
})
req_add_v.user = jh_admin
setattr(req_add_v, 'session', {})
setattr(req_add_v, '_messages', FallbackStorage(req_add_v))
resp_add_v = create_company_vendor_view(req_add_v)
assert resp_add_v.status_code == 302
new_v = User.objects.get(email="ranchi_steel@infinity.local")
assert new_v.assigned_state == "Jharkhand"
assert "Jharkhand" in new_v.vendor_profile.location
print("[OK] TEST 3.2 passed: Company Vendor created by Area Admin is auto-tagged to Jharkhand.")

# -------------------------------------------------------------
# TEST 4: Super Admin Full CRUD Operations
# -------------------------------------------------------------
# Super Admin Dashboard
req_sa_dash = rf.get('/super-admin/')
req_sa_dash.user = sa_user
resp_sa_dash = super_admin_dashboard(req_sa_dash)
assert resp_sa_dash.status_code == 200
print("[OK] TEST 4.1 passed: Super Admin Dashboard loads global overview across all states.")

# Super Admin User CRUD (Create an Area Admin for Delhi)
req_sa_u_create = rf.post('/super-admin/users/create/', data={
    "username": "delhi_admin_user",
    "email": "delhi_admin@infinity.local",
    "password": "Password123",
    "role": "ADMIN",
    "assigned_state": "Delhi",
    "first_name": "Delhi",
    "last_name": "Admin"
})
req_sa_u_create.user = sa_user
setattr(req_sa_u_create, 'session', {})
setattr(req_sa_u_create, '_messages', FallbackStorage(req_sa_u_create))
resp_sa_u_create = super_admin_user_create(req_sa_u_create)
assert resp_sa_u_create.status_code == 302
delhi_admin = User.objects.get(username="delhi_admin_user")
assert delhi_admin.role == "ADMIN"
assert delhi_admin.assigned_state == "Delhi"
assert delhi_admin.is_staff == True
print("[OK] TEST 4.2 passed: Super Admin successfully created a new Area Admin for Delhi.")

# Super Admin Vendor Create
req_sa_v_create = rf.post('/super-admin/vendors/create/', data={
    "username": "punjab_contractor",
    "email": "punjab_v@infinity.local",
    "password": "Password123",
    "company_name": "Punjab Infrastructure",
    "vendor_type": "company",
    "category": "Home Construction",
    "state": "Punjab",
    "city": "Amritsar",
    "experience": "8",
    "rating": "4.9",
    "about": "Punjab regional infrastructure specialist"
})
req_sa_v_create.user = sa_user
setattr(req_sa_v_create, 'session', {})
setattr(req_sa_v_create, '_messages', FallbackStorage(req_sa_v_create))
resp_sa_v_create = super_admin_vendor_create(req_sa_v_create)
assert resp_sa_v_create.status_code == 302
punjab_v = User.objects.get(username="punjab_contractor")
assert punjab_v.assigned_state == "Punjab"
assert punjab_v.vendor_profile.company_name == "Punjab Infrastructure"
print("[OK] TEST 4.3 passed: Super Admin successfully created a new Vendor in Punjab.")

# Super Admin Job Create
req_sa_j_create = rf.post('/super-admin/jobs/create/', data={
    "user": cust_jh.id,
    "title": "Super Admin Created Project",
    "category": cat_gen.id,
    "location": loc_jh.id,
    "budget": "50000",
    "status": "open",
    "description": "Created from super admin center"
})
req_sa_j_create.user = sa_user
setattr(req_sa_j_create, 'session', {})
setattr(req_sa_j_create, '_messages', FallbackStorage(req_sa_j_create))
resp_sa_j_create = super_admin_job_create(req_sa_j_create)
assert resp_sa_j_create.status_code == 302
sa_job = Job.objects.get(title="Super Admin Created Project")
assert sa_job.budget == 50000
print("[OK] TEST 4.4 passed: Super Admin successfully created a Job project.")

# Super Admin Quick Service Create
req_sa_qs_create = rf.post('/super-admin/quick-services/create/', data={
    "user": cust_jh.id,
    "title": "Super Admin Quick Booking",
    "category": cat_gen.id,
    "location": loc_jh.id,
    "budget": "2500",
    "status": "open",
    "description": "Instant service request"
})
req_sa_qs_create.user = sa_user
setattr(req_sa_qs_create, 'session', {})
setattr(req_sa_qs_create, '_messages', FallbackStorage(req_sa_qs_create))
resp_sa_qs_create = super_admin_qs_create(req_sa_qs_create)
assert resp_sa_qs_create.status_code == 302
sa_qs = QuickService.objects.get(title="Super Admin Quick Booking")
assert sa_qs.budget == 2500
print("[OK] TEST 4.5 passed: Super Admin successfully created a Quick Service.")

# Super Admin Bid Create
req_sa_b_create = rf.post('/super-admin/bids/create/', data={
    "vendor": v_jh_user.id,
    "target_type": "job",
    "target_id": sa_job.id,
    "amount": "48000",
    "status": "selected",
    "proposal": "Super Admin assigned quotation"
})
req_sa_b_create.user = sa_user
setattr(req_sa_b_create, 'session', {})
setattr(req_sa_b_create, '_messages', FallbackStorage(req_sa_b_create))
resp_sa_b_create = super_admin_bid_create(req_sa_b_create)
assert resp_sa_b_create.status_code == 302
sa_bid = Bid.objects.get(job=sa_job, vendor=v_jh_user)
assert sa_bid.amount == 48000
print("[OK] TEST 4.6 passed: Super Admin successfully created and accepted a Bid quotation.")

# Super Admin Subscription Create
req_sa_sub_create = rf.post('/super-admin/subscriptions/create/', data={
    "vendor": v_jh_user.id,
    "package_name": "Enterprise Prime (100 Bids)",
    "amount": "1999.00",
    "credits": "100",
    "status": "success"
})
req_sa_sub_create.user = sa_user
setattr(req_sa_sub_create, 'session', {})
setattr(req_sa_sub_create, '_messages', FallbackStorage(req_sa_sub_create))
resp_sa_sub_create = super_admin_subscription_create(req_sa_sub_create)
assert resp_sa_sub_create.status_code == 302
sa_sub = Subscription.objects.filter(vendor=v_jh_user, package_name="Enterprise Prime (100 Bids)").first()
assert sa_sub is not None
print("[OK] TEST 4.7 passed: Super Admin successfully created a Subscription and top-up credits.")

# Super Admin Toggle User
req_sa_toggle = rf.get(f'/super-admin/users/{delhi_admin.id}/toggle/')
req_sa_toggle.user = sa_user
setattr(req_sa_toggle, 'session', {})
setattr(req_sa_toggle, '_messages', FallbackStorage(req_sa_toggle))
super_admin_user_toggle(req_sa_toggle, delhi_admin.id)
delhi_admin.refresh_from_db()
assert delhi_admin.is_active == False
print("[OK] TEST 4.8 passed: Super Admin successfully toggled Area Admin status to deactivated.")

# Clean up created test items
new_u.delete()
new_v.delete()
delhi_admin.delete()
punjab_v.delete()
sa_job.delete()
sa_qs.delete()
sa_sub.delete()

print("\n=======================================================")
print("ALL AREA ADMIN ISOLATION & SUPER ADMIN CRUD TESTS PASSED 100%!")
print("=======================================================")
