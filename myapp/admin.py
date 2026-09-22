from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, VendorProfile, UserProfile, QuickService, Job, Bid, Subscription

from .models import CustomUser, UserProfile, VendorProfile, QuickService, Job, Bid, Subscription, Category, Location, Message

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

admin.site.register(UserProfile)
admin.site.register(Subscription)
admin.site.register(Message)
