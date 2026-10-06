import secrets
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('VENDOR', 'Vendor'),
        ('USER', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    assigned_state = models.CharField(max_length=100, blank=True, null=True, help_text="Assigned State/Territory for Area Admin")
    assigned_city = models.CharField(max_length=100, blank=True, null=True, help_text="Assigned City (optional) for Area Admin")

class VendorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_profile')
    vendor_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    
    VENDOR_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('company', 'Company Vendor'),
    )
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPE_CHOICES, default='vendor')
    employee_code = models.CharField(max_length=50, null=True, blank=True)
    employee_details = models.TextField(null=True, blank=True)
    
    # New Personal Details
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    experience = models.IntegerField(default=0)
    id_proof = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to='vendor_profiles/', null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    available_bids = models.IntegerField(default=5)
    registered_date = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=True, help_text="Is vendor currently accepting bookings?")

    def __str__(self):
        return self.company_name or self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.vendor_code:
            self.vendor_code = f"VEN{self.id:03d}"
            self.save(update_fields=['vendor_code'])

class VendorKYC(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Verified & Approved'),
        ('rejected', 'Rejected / Re-upload Required'),
    )
    vendor = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='kyc_document')
    id_type = models.CharField(max_length=50, choices=[('aadhaar', 'Aadhaar Card'), ('pan', 'PAN Card'), ('voter_id', 'Voter ID')])
    id_number = models.CharField(max_length=50)
    id_document_front = models.FileField(upload_to='kyc/id_docs/')
    id_document_back = models.FileField(upload_to='kyc/id_docs/', null=True, blank=True)
    business_license = models.FileField(upload_to='kyc/licenses/', null=True, blank=True)
    gst_certificate = models.FileField(upload_to='kyc/gst/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_kycs')
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.vendor.username} - KYC ({self.get_status_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='user_profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class CustomerAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, help_text="e.g. Home, Work, Other")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class QuickService(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('draft', 'Draft'),
    )
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vendor_services')
    title = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_packages = models.JSONField(default=list, blank=True, null=True, help_text="List of packages/variants e.g. [{'name': 'Haircut', 'price': 150}]")
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Vendor service latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Vendor service longitude")
    locality = models.CharField(max_length=255, null=True, blank=True, help_text="Colony/Locality name e.g. Lalpur, Doranda")
    service_radius_km = models.FloatField(default=10.0, help_text="Maximum service radius in km (default 10km)")
    image = models.ImageField(upload_to='quick_services/', null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True, help_text="Direct or preset image URL")
    inclusions = models.JSONField(default=list, blank=True, null=True, help_text="List of inclusions")
    exclusions = models.JSONField(default=list, blank=True, null=True, help_text="List of exclusions")
    tags = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} by {self.vendor.username}"

    @property
    def user(self):
        """Backward-compatibility alias for vendor"""
        return self.vendor

    @user.setter
    def user(self, val):
        self.vendor = val

    @property
    def budget(self):
        """Backward-compatibility alias for base_price"""
        return self.base_price

    @budget.setter
    def budget(self, val):
        self.base_price = val

class ServiceBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_bookings')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vendor_bookings')
    quick_service = models.ForeignKey(QuickService, on_delete=models.SET_NULL, null=True, related_name='bookings')
    package_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    service_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')])
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_notes = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.quick_service.title if self.quick_service else 'Service'}"

class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed'),
        ('selected', 'Vendor Selected'),
    )
    title = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    required_work = models.JSONField(default=list, blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)
    materials_details = models.TextField(blank=True, null=True)
    additional_requirements = models.TextField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    budget_type = models.CharField(max_length=50, blank=True, null=True)
    preferred_start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    required_time = models.CharField(max_length=100, blank=True, null=True)
    shift_availability = models.CharField(max_length=50, blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Job location latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Job location longitude")
    city = models.CharField(max_length=100, null=True, blank=True, help_text="Job city")
    state = models.CharField(max_length=100, null=True, blank=True, help_text="Job state")
    locality = models.CharField(max_length=255, null=True, blank=True, help_text="Colony/Locality name")
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_mobile = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='jobs')
    bids_count = models.IntegerField(default=0)
    max_bids = models.IntegerField(default=10, blank=True, null=True, help_text="Maximum allowed bids")
    min_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum allowed bid price")
    max_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum allowed bid price")
    assigned_vendor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs', help_text="Vendor assigned to this job")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Bid(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bids')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bids', null=True, blank=True)
    quick_service = models.ForeignKey('QuickService', on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor_base_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Net amount vendor receives upon completion")
    commission_percent_applied = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Platform commission % at bid time")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Platform commission fee in INR")
    cgst_percent_applied = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="CGST % applied")
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="CGST collected in INR")
    sgst_percent_applied = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="SGST % applied")
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="SGST collected in INR")
    flat_fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Flat convenience fee in INR")
    total_customer_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Final payable amount charged to customer")
    estimated_time = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    proposal = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='bid_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def display_vendor_payout(self):
        return self.vendor_base_amount if self.vendor_base_amount is not None else self.amount

    @property
    def display_customer_total(self):
        return self.total_customer_amount if self.total_customer_amount is not None else self.amount

    def __str__(self):
        target_title = self.job.title if self.job else 'Service'
        return f"{self.vendor.username} - {target_title}"

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    package_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits_added = models.IntegerField(default=15, help_text="Number of bid credits added with this package")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.vendor.username} - {self.package_name}"


class BidCreditTransaction(models.Model):
    TYPE_CHOICES = (
        ('purchased', 'Credits Purchased'),
        ('used', 'Bid Placed'),
        ('refund', 'Credit Refund'),
        ('bonus', 'Welcome / Bonus Credits'),
    )
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    credits = models.IntegerField(help_text="Positive for additions (+15), negative for usage (-1)")
    description = models.CharField(max_length=255)
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    related_subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.username} - {self.transaction_type}: {self.credits:+d}"


class VendorWallet(models.Model):
    vendor = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendor Wallet"
        verbose_name_plural = "Vendor Wallets"

    def __str__(self):
        return f"{self.vendor.username} Wallet (₹{self.available_balance})"


class WalletTransaction(models.Model):
    TXN_TYPE = (
        ('credit', 'Job Earnings'),
        ('debit', 'Payout Withdrawal'),
        ('commission', 'Commission Deduction'),
        ('refund', 'Refund / Adjustment'),
    )
    wallet = models.ForeignKey(VendorWallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TXN_TYPE)
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    related_quick_service = models.ForeignKey(QuickService, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.vendor.username} - {self.transaction_type}: ₹{self.amount}"


class PayoutRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('processing', 'Processing'),
        ('completed', 'Transferred / Paid'),
        ('rejected', 'Rejected'),
    )
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_method = models.CharField(max_length=20, choices=[('bank', 'Bank Transfer'), ('upi', 'UPI ID')])
    account_holder_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bank_reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="UTR / Transaction Ref")
    admin_remarks = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.vendor.username} - ₹{self.amount} ({self.get_status_display()})"


class DisputeTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent — Safety Concern'),
    )
    CATEGORY_CHOICES = (
        ('payment', 'Payment / Pricing Issue'),
        ('quality', 'Poor Work Quality / Incomplete'),
        ('noshow', 'No Show / Unreachable'),
        ('behavior', 'Misbehavior / Unprofessional Conduct'),
        ('delay', 'Delay in Execution / Missed Deadline'),
        ('platform', 'Platform or Account Issue'),
        ('other', 'Other Issue'),
    )

    ticket_id = models.CharField(max_length=30, unique=True, db_index=True)
    raised_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='filed_disputes')
    against_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_disputes')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes')
    quick_service = models.ForeignKey(QuickService, on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='quality')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    evidence_image = models.FileField(upload_to='disputes/evidence/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Dispute Ticket"
        verbose_name_plural = "Dispute Tickets"

    def __str__(self):
        return f"{self.ticket_id} - {self.subject} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            import random
            year = timezone.now().year
            rand_suffix = random.randint(1000, 9999)
            self.ticket_id = f"CMP-{year}-{rand_suffix}"
            while DisputeTicket.objects.filter(ticket_id=self.ticket_id).exists():
                rand_suffix = random.randint(1000, 9999)
                self.ticket_id = f"CMP-{year}-{rand_suffix}"
        super().save(*args, **kwargs)

    @property
    def related_item_label(self):
        if self.job:
            return f"JOB-{self.job.id:04d} · {self.job.title}"
        elif self.quick_service:
            return f"QS-{self.quick_service.id:04d} · {self.quick_service.title}"
        return "General / Account"


class DisputeMessage(models.Model):
    ticket = models.ForeignKey(DisputeTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dispute_messages')
    message = models.TextField()
    attachment = models.FileField(upload_to='disputes/evidence/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.sender.username} ({self.created_at.strftime('%d %b %H:%M')})"


class JobCompletionProof(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='completion_proof', null=True, blank=True)
    quick_service = models.OneToOneField(QuickService, on_delete=models.CASCADE, related_name='completion_proof', null=True, blank=True)
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_completion_proofs')
    photo_1 = models.ImageField(upload_to='jobs/proof/')
    photo_2 = models.ImageField(upload_to='jobs/proof/', null=True, blank=True)
    work_summary = models.TextField()
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-completed_at']
        verbose_name = "Job Completion Proof"
        verbose_name_plural = "Job Completion Proofs"

    def __str__(self):
        target = f"JOB-{self.job_id:04d}" if self.job else (f"QS-{self.quick_service_id:04d}" if self.quick_service else "General")
        return f"Completion Proof: {target} by {self.vendor.username}"


class ServiceReview(models.Model):
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('pending', 'Under Review'),
        ('hidden', 'Hidden'),
    )

    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    quick_service = models.ForeignKey(QuickService, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    booking = models.OneToOneField(ServiceBooking, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='written_reviews')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField(default=5)  # 1 to 5
    review_title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField()
    review_image = models.ImageField(upload_to='reviews/photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Service Review"
        verbose_name_plural = "Service Reviews"

    def __str__(self):
        return f"{self.rating}★ Review by {self.customer.username} for {self.vendor.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            from django.db.models import Avg
            profile = getattr(self.vendor, 'vendor_profile', None)
            if profile:
                avg = ServiceReview.objects.filter(vendor=self.vendor, status='published').aggregate(avg=Avg('rating'))['avg']
                if avg is not None:
                    profile.rating = round(avg, 1)
                    profile.save(update_fields=['rating'])
        except Exception:
            pass


class Category(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('job', 'Job'),
        ('quick_service', 'Quick Service'),
        ('both', 'Both'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='both')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Category.STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class State(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Location(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.city}, {self.state}"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    job = models.ForeignKey('Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    quick_service = models.ForeignKey('QuickService', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    content = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.created_at}"

class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ('login', 'Login'),
        ('signup', 'Signup'),
        ('general', 'General'),
    )
    mobile = models.CharField(max_length=50, db_index=True)
    otp = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='general')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.mobile} - {self.otp} ({self.purpose})"


class AuthToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='auth_tokens')
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(24)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.key[:8]}..."



class GlobalSettings(models.Model):
    site_title = models.CharField(max_length=255, default='Sugu')
    contact_email = models.EmailField(default='support@sugu.com')
    support_phone = models.CharField(max_length=20, default='+91 0000000000')
    maintenance_mode = models.BooleanField(default=False)
    platform_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Platform commission cut %")
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="Central GST % applied on platform commission")
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="State GST % applied on platform commission")
    platform_flat_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Fixed convenience / platform flat fee in INR")
    tax_calculation_mode = models.CharField(
        max_length=20,
        choices=[('commission_only', 'Tax on Platform Fee Only'), ('total_invoice', 'Tax on Total Service Invoice')],
        default='commission_only',
        help_text="Choose whether GST applies to platform commission or total customer invoice"
    )
    single_bid_cost = models.DecimalField(max_digits=8, decimal_places=2, default=20.00, help_text="Cost of a single bid credit in INR")
    free_starter_bids = models.IntegerField(default=5, help_text="Free starter bids given to newly registered vendors")
    min_bids_per_job = models.IntegerField(default=1, help_text="Bids deducted per job quotation proposal")

    # Quick Services Dedicated Pricing & Tax Levers (Does not affect custom jobs or bidding)
    qs_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Quick Services Platform Commission Cut %")
    qs_cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="Quick Services Central GST %")
    qs_sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00, help_text="Quick Services State GST %")
    qs_flat_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Quick Services Platform Flat Fee in INR")
    qs_tax_mode = models.CharField(
        max_length=20,
        choices=[('commission_only', 'Tax on Platform Cut Only'), ('total_invoice', 'Tax on Total Service Price')],
        default='commission_only',
        help_text="Choose whether GST applies to platform cut only or full service price for Quick Services"
    )

    class Meta:
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return "Platform Settings"

    def get_qs_commission_percent(self):
        if self.qs_commission_percent is not None:
            return float(self.qs_commission_percent)
        return float(self.platform_commission_percent or 10.0)

    def get_qs_cgst_percent(self):
        if self.qs_cgst_percent is not None:
            return float(self.qs_cgst_percent)
        return float(self.cgst_percent or 9.0)

    def get_qs_sgst_percent(self):
        if self.qs_sgst_percent is not None:
            return float(self.qs_sgst_percent)
        return float(self.sgst_percent or 9.0)

    def get_qs_flat_fee(self):
        if self.qs_flat_fee is not None:
            return float(self.qs_flat_fee)
        return float(self.platform_flat_fee or 0.0)

    def get_qs_tax_mode(self):
        return self.qs_tax_mode or self.tax_calculation_mode or 'commission_only'

    def calculate_qs_customer_price(self, base_vendor_payout):
        """
        Calculates final customer listed price from vendor base payout.
        Formula:
          comm = base * (comm_pct / 100) + flat_fee
          taxable = comm if tax_mode == 'commission_only' else (base + comm)
          cgst = taxable * (cgst_pct / 100)
          sgst = taxable * (sgst_pct / 100)
          customer_price = round(base + comm + cgst + sgst)
        """
        try:
            base = float(base_vendor_payout or 0.0)
        except (ValueError, TypeError):
            base = 0.0
        
        comm_pct = self.get_qs_commission_percent()
        cgst_pct = self.get_qs_cgst_percent()
        sgst_pct = self.get_qs_sgst_percent()
        flat = self.get_qs_flat_fee()
        mode = self.get_qs_tax_mode()

        comm = (base * (comm_pct / 100.0)) + flat
        taxable = comm if mode == 'commission_only' else (base + comm)
        cgst = taxable * (cgst_pct / 100.0)
        sgst = taxable * (sgst_pct / 100.0)
        customer_price = round(base + comm + cgst + sgst)

        return {
            'vendor_payout': round(base, 2),
            'commission': round(comm, 2),
            'cgst': round(cgst, 2),
            'sgst': round(sgst, 2),
            'total_tax': round(cgst + sgst, 2),
            'customer_price': customer_price,
            'commission_percent': comm_pct,
            'cgst_percent': cgst_pct,
            'sgst_percent': sgst_pct,
            'flat_fee': flat,
            'tax_mode': mode
        }

    def split_qs_final_total(self, final_customer_total):
        """
        Splits an all-inclusive customer payment into SuperAdmin cut + taxes and Vendor Wallet payout.
        Example: Customer pays ₹893:
          commission = round(893 * (comm_pct / 100), 2)
          cgst = round(commission * (cgst_pct / 100), 2)
          sgst = round(commission * (sgst_pct / 100), 2)
          superadmin_total = commission + cgst + sgst + flat_fee
          vendor_payout = round(893 - superadmin_total, 2)
        """
        try:
            total = float(final_customer_total or 0.0)
        except (ValueError, TypeError):
            total = 0.0

        comm_pct = self.get_qs_commission_percent()
        cgst_pct = self.get_qs_cgst_percent()
        sgst_pct = self.get_qs_sgst_percent()
        flat = self.get_qs_flat_fee()
        mode = self.get_qs_tax_mode()

        comm = round((total * (comm_pct / 100.0)) + flat, 2)
        if mode == 'commission_only':
            cgst = round(comm * (cgst_pct / 100.0), 2)
            sgst = round(comm * (sgst_pct / 100.0), 2)
        else:
            cgst = round(total * (cgst_pct / 100.0), 2)
            sgst = round(total * (sgst_pct / 100.0), 2)

        total_tax = round(cgst + sgst, 2)
        superadmin_total = round(comm + total_tax, 2)
        vendor_payout = round(max(0.0, total - superadmin_total), 2)

        return {
            'total_customer_payable': total,
            'customer_price': total,
            'vendor_payout': vendor_payout,
            'commission': comm,
            'cgst': cgst,
            'sgst': sgst,
            'total_tax': total_tax,
            'flat_fee': flat,
            'superadmin_share': superadmin_total,
            'commission_percent': comm_pct,
            'cgst_percent': cgst_pct,
            'sgst_percent': sgst_pct,
            'tax_mode': mode,
        }



class PlatformRevenueLedger(models.Model):
    related_bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True, related_name='revenue_ledgers')
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    related_quick_service = models.ForeignKey('QuickService', on_delete=models.SET_NULL, null=True, blank=True)
    related_booking = models.ForeignKey('ServiceBooking', on_delete=models.SET_NULL, null=True, blank=True, related_name='revenue_ledgers')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='settled_commissions')
    vendor_payout = models.DecimalField(max_digits=10, decimal_places=2, help_text="Net amount credited to vendor wallet")
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, help_text="Platform commission earned")
    cgst_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Central GST collected")
    sgst_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="State GST collected")
    flat_fee_collected = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Flat fee collected")
    total_customer_paid = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount paid by customer")
    settled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-settled_at']
        verbose_name = "Platform Revenue Ledger"
        verbose_name_plural = "Platform Revenue Ledgers"

    def __str__(self):
        total_tax = (self.cgst_collected or 0) + (self.sgst_collected or 0)
        return f"Ledger #{self.id} - Comm: ₹{self.platform_commission} | Tax: ₹{total_tax} | Vendor: ₹{self.vendor_payout}"


class BidPlan(models.Model):
    name = models.CharField(max_length=150, help_text="Plan Name e.g. Starter Pack, Value Pack, Pro Contractor")
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text="Short subtitle e.g. For occasional bidding")
    credits = models.PositiveIntegerField(help_text="Number of bids / credits provided (e.g. 5, 10, 30)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR (e.g. 100.00, 200.00, 500.00)")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price for strikethrough comparison")
    is_popular = models.BooleanField(default=False, help_text="Highlight with Most Popular / Best Value badge")
    is_active = models.BooleanField(default=True, help_text="Enable or disable this plan for vendors")
    order = models.IntegerField(default=0, help_text="Display sort order")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', 'price']
        verbose_name = "Bid Plan"
        verbose_name_plural = "Bid Plans"

    def __str__(self):
        return f"{self.name} - {self.credits} Bids (₹{self.price})"

    @property
    def cost_per_bid(self):
        if self.credits and self.credits > 0:
            return round(float(self.price) / float(self.credits), 1)
        return float(self.price)



# ==============================================================================
# LANDING PAGE CMS & DYNAMIC CONTENT MODELS
# ==============================================================================

class SiteBranding(models.Model):
    site_title = models.CharField(max_length=255, default='Sugu')
    tagline = models.CharField(max_length=255, default='Instant Home Services & Custom Project Bidding Marketplace')
    logo = models.ImageField(upload_to='cms/branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='cms/branding/', null=True, blank=True)
    contact_email = models.EmailField(default='support@sugu.com')
    support_phone = models.CharField(max_length=50, default='+91 98765 43210')
    address = models.CharField(max_length=255, default='Main Road, Ranchi, Jharkhand, India')
    facebook_url = models.URLField(blank=True, null=True, default='https://facebook.com')
    instagram_url = models.URLField(blank=True, null=True, default='https://instagram.com')
    linkedin_url = models.URLField(blank=True, null=True, default='https://linkedin.com')
    twitter_url = models.URLField(blank=True, null=True, default='https://twitter.com')
    youtube_url = models.URLField(blank=True, null=True, default='https://youtube.com')
    copyright_text = models.CharField(max_length=255, default='© 2026 Sugu. All rights reserved.')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site Branding"

    def __str__(self):
        return self.site_title


class HeroSection(models.Model):
    badge_text = models.CharField(max_length=100, default='DUAL-ENGINE MARKETPLACE')
    headline = models.CharField(max_length=255, default='Book instant home pros or get competitive bids for custom projects.')
    subtext = models.TextField(default="India's smartest service network. Book verified technicians at upfront prices in 60 seconds, or post major contracting jobs and compare bids side-by-side.")
    hero_image = models.ImageField(upload_to='cms/hero/', null=True, blank=True)
    cta_primary_text = models.CharField(max_length=100, default='Post a Quick Service')
    cta_primary_url = models.CharField(max_length=255, default='/user/quick-services/create.html')
    cta_secondary_text = models.CharField(max_length=100, default='Post a Custom Job')
    cta_secondary_url = models.CharField(max_length=255, default='/user/jobs/create.html')
    
    # Key Stats
    stat1_number = models.CharField(max_length=50, default='60s')
    stat1_label = models.CharField(max_length=100, default='Instant Pro Matching')
    stat2_number = models.CharField(max_length=50, default='15k+')
    stat2_label = models.CharField(max_length=100, default='Verified Technicians')
    stat3_number = models.CharField(max_length=50, default='100%')
    stat3_label = models.CharField(max_length=100, default='Price Protection')
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return self.headline[:50]


class QuickServiceCard(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='cms/quick_services/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=299.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=100, default='45 Mins')
    category_tag = models.CharField(max_length=100, default='Plumbing')
    badge_text = models.CharField(max_length=100, default='Instant', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class FeaturedProjectCard(models.Model):
    title = models.CharField(max_length=255)
    category_name = models.CharField(max_length=100, default='Renovation')
    budget_range = models.CharField(max_length=100, default='₹45,000 - ₹60,000')
    location = models.CharField(max_length=100, default='Ranchi, Jharkhand')
    timeline = models.CharField(max_length=100, default='30 Days')
    vendor_quote_preview = models.CharField(max_length=255, default='Lowest bid: ₹42,500 · 3 Verified Contractors quoted')
    bids_count = models.IntegerField(default=5)
    status_tag = models.CharField(max_length=50, default='Active Bidding')
    image = models.ImageField(upload_to='cms/featured_projects/', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class PackageCard(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=999.00)
    price_unit = models.CharField(max_length=50, default='/ Project')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    feature_bullets = models.TextField(help_text="Enter features separated by newlines", default="Complete deep inspection\nStandard warranty included\nVerified background-checked pros")
    filter_tag = models.CharField(max_length=50, default='All', help_text="e.g. All, Plumbing, Electrical, Cleaning")
    cta_label = models.CharField(max_length=100, default='Book Package')
    cta_url = models.CharField(max_length=255, default='/user/quick-services/create.html')
    is_popular = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def get_features_list(self):
        return [f.strip() for f in self.feature_bullets.split('\n') if f.strip()]

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    client_name = models.CharField(max_length=255)
    client_role_or_company = models.CharField(max_length=255, default='Homeowner, Ranchi')
    avatar = models.ImageField(upload_to='cms/testimonials/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_text = models.TextField(default='Amazing experience! The technician arrived in under 30 minutes and resolved our electrical issue with full transparent pricing.')
    service_taken = models.CharField(max_length=100, default='Emergency Electrical Repair')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.rating}★"


class TrustMetric(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, help_text="e.g. Aadhaar & Police Verified")
    description = models.TextField(null=True, blank=True, help_text="Detailed trust point description")
    badge_text = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. 100% of active pros verified")
    icon_svg = models.TextField(null=True, blank=True, help_text="SVG markup for icon")
    icon_class = models.CharField(max_length=100, default='fa-solid fa-shield-halved', help_text='FontAwesome icon class')
    stat_number = models.CharField(max_length=50, default='100%')
    label = models.CharField(max_length=100, default='Verified & Background Checked')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f"{self.stat_number} {self.label}"


