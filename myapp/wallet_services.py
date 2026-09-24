from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    VendorWallet, WalletTransaction, PayoutRequest, 
    GlobalSettings, Job, QuickService, Bid, CustomUser
)

def get_or_create_wallet(vendor):
    """Returns the VendorWallet for the vendor, creating one if needed."""
    wallet, _ = VendorWallet.objects.get_or_create(vendor=vendor)
    return wallet

def get_platform_commission_percent():
    """Fetches the global platform commission percentage."""
    settings = GlobalSettings.objects.first()
    if settings and settings.platform_commission_percent is not None:
        return Decimal(str(settings.platform_commission_percent))
    return Decimal('10.00')

def settle_job_completion(job=None, quick_service=None, vendor=None, custom_amount=None):
    """
    Settles earnings for a completed Job or QuickService.
    Applies the platform commission deduction, credits the vendor's wallet,
    and logs itemized transactions. Prevents duplicate settlements.
    """
    target = job or quick_service
    if not target:
        return False, "No job or quick service provided for settlement."

    title = target.title
    is_job = bool(job)

    # Determine winning vendor if not explicitly given
    if not vendor:
        if is_job:
            vendor = target.assigned_vendor
            if not vendor:
                sel_bid = Bid.objects.filter(job=job, status__in=['selected', 'completed']).first()
                if sel_bid:
                    vendor = sel_bid.vendor
        else:
            sel_bid = Bid.objects.filter(quick_service=quick_service, status__in=['selected', 'completed']).first()
            if sel_bid:
                vendor = sel_bid.vendor

    if not vendor:
        return False, f"Could not determine the vendor to settle payment for '{title}'."

    wallet = get_or_create_wallet(vendor)

    # Check for existing settlement transaction to avoid double crediting
    existing = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='credit'
    )
    if is_job:
        existing = existing.filter(related_job=job)
    else:
        existing = existing.filter(related_quick_service=quick_service)

    if existing.exists():
        return False, f"Earnings for '{title}' have already been settled to {vendor.username}'s wallet."

    # Determine agreed gross amount
    if custom_amount is not None:
        gross_amount = Decimal(str(custom_amount))
    else:
        # Check winning bid first
        sel_bid = None
        if is_job:
            sel_bid = Bid.objects.filter(job=job, status__in=['selected', 'completed']).first()
        else:
            sel_bid = Bid.objects.filter(quick_service=quick_service, status__in=['selected', 'completed']).first()

        if sel_bid and sel_bid.amount:
            gross_amount = Decimal(str(sel_bid.amount))
        elif target.budget:
            gross_amount = Decimal(str(target.budget))
        else:
            gross_amount = Decimal('0.00')

    if gross_amount <= Decimal('0.00'):
        return False, "Settlement amount must be greater than zero."

    commission_percent = get_platform_commission_percent()
    commission_amount = (gross_amount * commission_percent / Decimal('100.00')).quantize(Decimal('0.01'))
    net_earning = gross_amount - commission_amount

    with transaction.atomic():
        # Update wallet balance
        wallet.available_balance += net_earning
        wallet.total_earned += net_earning
        wallet.save()

        # Log Gross Credit Transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=gross_amount,
            transaction_type='credit',
            related_job=job,
            related_quick_service=quick_service,
            description=f"Earnings from completed {'Job' if is_job else 'Quick Service'}: '{title}'"
        )

        # Log Commission Deduction Transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=commission_amount,
            transaction_type='commission',
            related_job=job,
            related_quick_service=quick_service,
            description=f"Platform Commission ({commission_percent}%) on '{title}'"
        )

    return True, f"Successfully settled ₹{net_earning:.2f} (Gross ₹{gross_amount:.2f} - ₹{commission_amount:.2f} fee) to {vendor.username}."

def request_payout(vendor, amount, payout_method, account_holder_name=None, 
                   account_number=None, ifsc_code=None, bank_name=None, upi_id=None):
    """
    Submits a vendor withdrawal request and places funds on hold from available balance.
    """
    wallet = get_or_create_wallet(vendor)
    req_amount = Decimal(str(amount)).quantize(Decimal('0.01'))

    if req_amount < Decimal('100.00'):
        return False, "Minimum payout request amount is ₹100.00."

    if req_amount > wallet.available_balance:
        return False, f"Insufficient balance. Your available balance is ₹{wallet.available_balance:.2f}."

    if payout_method == 'bank':
        if not account_number or not ifsc_code:
            return False, "Account number and IFSC code are required for bank transfer."
    elif payout_method == 'upi':
        if not upi_id or '@' not in upi_id:
            return False, "A valid UPI ID is required (e.g. username@upi)."
    else:
        return False, "Invalid payout method selected."

    with transaction.atomic():
        # Deduct from available balance immediately to prevent double spending
        wallet.available_balance -= req_amount
        wallet.save()

        payout = PayoutRequest.objects.create(
            vendor=vendor,
            amount=req_amount,
            payout_method=payout_method,
            account_holder_name=account_holder_name or vendor.get_full_name() or vendor.username,
            account_number=account_number,
            ifsc_code=ifsc_code,
            bank_name=bank_name,
            upi_id=upi_id,
            status='pending'
        )

    return True, payout

def approve_payout(payout_request, admin_user, bank_reference_number=None, remarks=None):
    """
    Super Admin or Area Admin marks a payout request as transferred/paid.
    """
    if payout_request.status != 'pending':
        return False, f"Payout #{payout_request.id} is already {payout_request.get_status_display()}."

    wallet = get_or_create_wallet(payout_request.vendor)

    with transaction.atomic():
        wallet.total_withdrawn += payout_request.amount
        wallet.save()

        payout_request.status = 'completed'
        payout_request.bank_reference_number = bank_reference_number or f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payout_request.admin_remarks = remarks
        payout_request.processed_at = timezone.now()
        payout_request.processed_by = admin_user
        payout_request.save()

        # Log Debit Transaction
        ref_text = f"UTR/Ref: {payout_request.bank_reference_number}"
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=payout_request.amount,
            transaction_type='debit',
            description=f"Withdrawal settlement to {payout_request.get_payout_method_display()} ({ref_text})"
        )

    return True, f"Payout #{payout_request.id} for ₹{payout_request.amount:.2f} approved and marked as transferred."

def reject_payout(payout_request, admin_user, remarks="Payout request rejected by administration."):
    """
    Super Admin or Area Admin rejects a payout request and refunds the money back to the vendor's available balance.
    """
    if payout_request.status != 'pending':
        return False, f"Payout #{payout_request.id} is already {payout_request.get_status_display()}."

    wallet = get_or_create_wallet(payout_request.vendor)

    with transaction.atomic():
        # Refund back to available balance
        wallet.available_balance += payout_request.amount
        wallet.save()

        payout_request.status = 'rejected'
        payout_request.admin_remarks = remarks
        payout_request.processed_at = timezone.now()
        payout_request.processed_by = admin_user
        payout_request.save()

        # Log Refund Transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=payout_request.amount,
            transaction_type='refund',
            description=f"Refund: Payout #{payout_request.id} rejected ({remarks})"
        )

    return True, f"Payout #{payout_request.id} rejected and ₹{payout_request.amount:.2f} refunded to vendor wallet."
