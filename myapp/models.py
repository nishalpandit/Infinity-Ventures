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

class VendorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.vendor.username} - {self.job.title}"

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

