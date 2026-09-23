from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, UserProfile, VendorProfile, QuickService, Job,
    Bid, Subscription, Category, Location, Message, GlobalSettings,
    SiteBranding, HeroSection, QuickServiceCard, FeaturedProjectCard,
    PackageCard, Testimonial, TrustMetric
)

@admin.action(description='Suspend selected users')
def suspend_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description='Activate selected users')
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
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
