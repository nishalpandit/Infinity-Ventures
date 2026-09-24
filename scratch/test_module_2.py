import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from myapp.models import (
    CustomUser, Job, QuickService, Category, Location, Bid,
    VendorWallet, WalletTransaction, PayoutRequest, GlobalSettings
)
from myapp.wallet_services import (
    get_or_create_wallet, settle_job_completion, request_payout,
    approve_payout, reject_payout, get_platform_commission_percent
)
from myapp.views import dashboard_view
from myapp.super_admin_views import (
    super_admin_payouts, super_admin_payout_approve, super_admin_payout_reject
)

User = get_user_model()

print("--- STARTING MODULE 2 VALIDATION ---")

# 1. Setup Test Users
vendor_user, _ = User.objects.get_or_create(
    username="test_wallet_vendor",
    defaults={"role": "VENDOR", "email": "vendor@testwallet.com"}
)
vendor_user.set_password("pass1234")
vendor_user.role = "VENDOR"
vendor_user.save()

customer_user, _ = User.objects.get_or_create(
    username="test_wallet_customer",
    defaults={"role": "USER", "email": "customer@testwallet.com"}
)
customer_user.set_password("pass1234")
customer_user.save()

super_admin, _ = User.objects.get_or_create(
    username="test_wallet_admin",
    defaults={"role": "ADMIN", "is_superuser": True, "is_staff": True, "email": "admin@testwallet.com"}
)
super_admin.is_superuser = True
super_admin.save()

# Ensure GlobalSettings exists
settings_obj, _ = GlobalSettings.objects.get_or_create(pk=1)
settings_obj.platform_commission_percent = Decimal('10.00')
settings_obj.save()

# Reset vendor wallet for clean test
wallet = get_or_create_wallet(vendor_user)
wallet.available_balance = Decimal('0.00')
wallet.total_earned = Decimal('0.00')
wallet.total_withdrawn = Decimal('0.00')
wallet.save()
wallet.transactions.all().delete()
PayoutRequest.objects.filter(vendor=vendor_user).delete()

print(f"[OK] Test users & fresh wallet initialized. Vendor: {vendor_user.username}")

# 2. Test Commission & Job Settlement
category, _ = Category.objects.get_or_create(name="Plumbing Services")
location, _ = Location.objects.get_or_create(state="Jharkhand", city="Ranchi")

test_job = Job.objects.create(
    title="Luxury Bathroom Fitting Project",
    user=customer_user,
    category=category,
    location=location,
    budget=Decimal('5000.00'),
    assigned_vendor=vendor_user,
    status='open'
)

# Place winning bid
winning_bid = Bid.objects.create(
    vendor=vendor_user,
    job=test_job,
    amount=Decimal('5000.00'),
    status='selected'
)

test_job.status = 'completed'
test_job.save()

settled, msg = settle_job_completion(job=test_job)
assert settled, f"Settlement failed: {msg}"
print(f"[OK] Job Settlement: {msg}")

# Verify Wallet Numbers:
# Gross = 5000.00, Commission (10%) = 500.00, Net = 4500.00
wallet.refresh_from_db()
assert wallet.available_balance == Decimal('4500.00'), f"Expected 4500.00, got {wallet.available_balance}"
assert wallet.total_earned == Decimal('4500.00'), f"Expected 4500.00, got {wallet.total_earned}"
print(f"[OK] Wallet balance correctly credited: ₹{wallet.available_balance:.2f}")

# Check itemized transactions
txns = wallet.transactions.all()
assert txns.count() == 2, f"Expected 2 transactions (gross + commission), got {txns.count()}"
credit_txn = txns.filter(transaction_type='credit').first()
comm_txn = txns.filter(transaction_type='commission').first()
assert credit_txn.amount == Decimal('5000.00')
assert comm_txn.amount == Decimal('500.00')
print("[OK] Transaction ledger has gross credit (₹5000) and commission deduction (₹500)")

# Verify duplicate settlement protection
settled_dup, dup_msg = settle_job_completion(job=test_job)
assert not settled_dup, "Duplicate settlement should have been blocked!"
print(f"[OK] Duplicate settlement prevention active: {dup_msg}")

# 3. Test Payout Request (Withdrawal)
# Try requesting more than available balance
bad_ok, bad_msg = request_payout(vendor_user, Decimal('6000.00'), 'bank', account_number="123456", ifsc_code="SBIN001")
assert not bad_ok, "Should fail when withdrawing more than available balance"
print("[OK] Overdraft withdrawal properly rejected")

# Try requesting valid amount: ₹2000 via Bank
req_ok, payout_req = request_payout(
    vendor_user,
    Decimal('2000.00'),
    'bank',
    account_holder_name="Test Vendor Pvt Ltd",
    account_number="112233445566",
    ifsc_code="SBIN0001234",
    bank_name="State Bank of India"
)
assert req_ok, f"Valid payout request failed: {payout_req}"
wallet.refresh_from_db()
assert wallet.available_balance == Decimal('2500.00'), f"Available balance should be 2500 after hold, got {wallet.available_balance}"
print(f"[OK] Payout request #PAY-{payout_req.id} placed. Balance held: new available = ₹{wallet.available_balance:.2f}")

# 4. Test Super Admin Approval with UTR
app_ok, app_msg = approve_payout(payout_req, super_admin, bank_reference_number="UTR-9988776655", remarks="Processed via RTGS")
assert app_ok, f"Approval failed: {app_msg}"
payout_req.refresh_from_db()
wallet.refresh_from_db()
assert payout_req.status == 'completed'
assert payout_req.bank_reference_number == "UTR-9988776655"
assert wallet.total_withdrawn == Decimal('2000.00')
print(f"[OK] Super Admin Approved: {app_msg}. Total Withdrawn = ₹{wallet.total_withdrawn:.2f}")

# 5. Test Payout Request Rejection with Automatic Refund
req2_ok, payout_req2 = request_payout(
    vendor_user,
    Decimal('1000.00'),
    'upi',
    upi_id="vendor@okhdfcbank"
)
assert req2_ok
wallet.refresh_from_db()
assert wallet.available_balance == Decimal('1500.00')

# Super Admin Rejects with Reason
rej_ok, rej_msg = reject_payout(payout_req2, super_admin, remarks="Invalid UPI VPA handle")
assert rej_ok, f"Rejection failed: {rej_msg}"
payout_req2.refresh_from_db()
wallet.refresh_from_db()
assert payout_req2.status == 'rejected'
assert wallet.available_balance == Decimal('2500.00'), f"Expected refund back to 2500, got {wallet.available_balance}"
print(f"[OK] Payout Rejection & Wallet Refund verified: {rej_msg}. Balance restored to ₹{wallet.available_balance:.2f}")

# 6. Test HTTP Endpoints via Django RequestFactory
factory = RequestFactory()

# Vendor Wallet Page View
req_v = factory.get('/vendor/wallet/index.html')
req_v.user = vendor_user
resp_v = dashboard_view(req_v, 'vendor/wallet/index')
assert resp_v.status_code == 200, f"Vendor wallet HTTP failed: {resp_v.status_code}"
content_v = resp_v.content.decode('utf-8')
assert "Vendor Wallet &amp; Payouts" in content_v or "Vendor Wallet" in content_v
assert "Transaction Ledger" in content_v
assert "Payout Requests" in content_v
print("[OK] Vendor Wallet UI endpoint /vendor/wallet/index renders successfully (HTTP 200)")

# Super Admin Payouts Hub
req_sa = factory.get('/super-admin/payouts/')
req_sa.user = super_admin
resp_sa = super_admin_payouts(req_sa)
assert resp_sa.status_code == 200, f"Super Admin payouts HTTP failed: {resp_sa.status_code}"
content_sa = resp_sa.content.decode('utf-8')
assert "Vendor Payout &amp; Settlement Hub" in content_sa or "Payouts" in content_sa
assert "UTR-9988776655" in content_sa
print("[OK] Super Admin Payouts Hub /super-admin/payouts/ renders successfully (HTTP 200)")

print("--- ALL MODULE 2 TESTS PASSED PERFECTLY! ---")
