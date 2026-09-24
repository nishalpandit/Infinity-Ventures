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
    registered_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.company_name or self.user.username

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
    profile_image = models.ImageField(upload_to='user_profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class QuickService(models.Model):
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
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    shift_availability = models.CharField(max_length=50, blank=True, null=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    additional_requirements = models.TextField(blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_mobile = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quick_services')
    bids_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

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
    quick_service = models.ForeignKey(QuickService, on_delete=models.CASCADE, related_name='bids', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    proposal = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='bid_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        target_title = self.job.title if self.job else (self.quick_service.title if self.quick_service else 'Service')
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.vendor.username} - {self.package_name}"

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
    site_title = models.CharField(max_length=255, default='Infinity Ventures')
    contact_email = models.EmailField(default='support@infinityventures.com')
    support_phone = models.CharField(max_length=20, default='+91 0000000000')
    maintenance_mode = models.BooleanField(default=False)
    platform_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return "Platform Settings"


# ==============================================================================
# LANDING PAGE CMS & DYNAMIC CONTENT MODELS
# ==============================================================================

class SiteBranding(models.Model):
    site_title = models.CharField(max_length=255, default='Infinity Ventures')
    tagline = models.CharField(max_length=255, default='Instant Home Services & Custom Project Bidding Marketplace')
    logo = models.ImageField(upload_to='cms/branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='cms/branding/', null=True, blank=True)
    contact_email = models.EmailField(default='support@infinityventures.com')
    support_phone = models.CharField(max_length=50, default='+91 98765 43210')
    address = models.CharField(max_length=255, default='Main Road, Ranchi, Jharkhand, India')
    facebook_url = models.URLField(blank=True, null=True, default='https://facebook.com')
    instagram_url = models.URLField(blank=True, null=True, default='https://instagram.com')
    linkedin_url = models.URLField(blank=True, null=True, default='https://linkedin.com')
    twitter_url = models.URLField(blank=True, null=True, default='https://twitter.com')
    youtube_url = models.URLField(blank=True, null=True, default='https://youtube.com')
    copyright_text = models.CharField(max_length=255, default='© 2026 Infinity Ventures. All rights reserved.')
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
    icon_class = models.CharField(max_length=100, default='fa-solid fa-shield-halved', help_text='FontAwesome icon class')
    stat_number = models.CharField(max_length=50, default='100%')
    label = models.CharField(max_length=100, default='Verified & Background Checked')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.stat_number} {self.label}"

