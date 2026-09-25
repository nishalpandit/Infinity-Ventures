from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, UserProfile, VendorProfile, QuickService, Job,
    Bid, Subscription, Category, Location, Message, GlobalSettings,
    SiteBranding, HeroSection, QuickServiceCard, FeaturedProjectCard,
    PackageCard, Testimonial, TrustMetric, VendorWallet, WalletTransaction, PayoutRequest,
    DisputeTicket, DisputeMessage, JobCompletionProof, ServiceReview
)

@admin.action(description='Suspend selected users')
def suspend_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description='Activate selected users')
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'assigned_state', 'is_active')
    list_filter = ('role', 'assigned_state', 'is_active')
    search_fields = ('username', 'email', 'assigned_state', 'assigned_city')
    actions = [suspend_users, activate_users]

admin.site.register(CustomUser, CustomUserAdmin)

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'vendor_type', 'rating')
    list_filter = ('vendor_type',)
    search_fields = ('company_name', 'user__username', 'user__email')

admin.site.register(VendorProfile, VendorProfileAdmin)

class QuickServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'user__username')

admin.site.register(QuickService, QuickServiceAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'user__username')

admin.site.register(Job, JobAdmin)

class BidAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('vendor__username',)

admin.site.register(Bid, BidAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'status')
    list_filter = ('service_type', 'status')
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'status')
    list_filter = ('state', 'status')
    search_fields = ('city',)

admin.site.register(Location, LocationAdmin)

# CMS Model Registrations
@admin.register(SiteBranding)
class SiteBrandingAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'contact_email', 'support_phone', 'updated_at')

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('badge_text', 'headline', 'updated_at')

@admin.register(QuickServiceCard)
class QuickServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_tag', 'price', 'discount_price', 'badge_text', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category_tag', 'is_active')
    search_fields = ('title', 'category_tag')

@admin.register(FeaturedProjectCard)
class FeaturedProjectCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_name', 'budget_range', 'location', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category_name', 'is_active')
    search_fields = ('title', 'category_name', 'location')

@admin.register(PackageCard)
class PackageCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'filter_tag', 'is_popular', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'is_popular')
    list_filter = ('filter_tag', 'is_active', 'is_popular')
    search_fields = ('title', 'filter_tag')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_role_or_company', 'rating', 'service_taken', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('rating', 'is_active')
    search_fields = ('client_name', 'service_taken')

@admin.register(TrustMetric)
class TrustMetricAdmin(admin.ModelAdmin):
    list_display = ('stat_number', 'label', 'icon_class', 'order', 'is_active')
    list_editable = ('order', 'is_active')

admin.site.register(UserProfile)
admin.site.register(Subscription)
admin.site.register(Message)
admin.site.register(GlobalSettings)

class VendorWalletAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'available_balance', 'total_earned', 'total_withdrawn', 'updated_at')
    search_fields = ('vendor__username', 'vendor__email')

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('wallet__vendor__username', 'description')

class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'payout_method', 'status', 'bank_reference_number', 'requested_at')
    list_filter = ('status', 'payout_method')
    search_fields = ('vendor__username', 'bank_reference_number', 'account_number', 'upi_id')

admin.site.register(VendorWallet, VendorWalletAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)
admin.site.register(PayoutRequest, PayoutRequestAdmin)

class DisputeMessageInline(admin.TabularInline):
    model = DisputeMessage
    extra = 1

@admin.register(DisputeTicket)
class DisputeTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'subject', 'raised_by', 'against_user', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_id', 'subject', 'description', 'raised_by__username', 'against_user__username')
    inlines = [DisputeMessageInline]

@admin.register(DisputeMessage)
class DisputeMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'created_at')
    search_fields = ('ticket__ticket_id', 'sender__username', 'message')

@admin.register(JobCompletionProof)
class JobCompletionProofAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'job', 'quick_service', 'completed_at')
    search_fields = ('vendor__username', 'work_summary')

@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'customer', 'rating', 'review_title', 'status', 'created_at')
    list_filter = ('rating', 'status')
    search_fields = ('vendor__username', 'customer__username', 'review_title', 'comment')


