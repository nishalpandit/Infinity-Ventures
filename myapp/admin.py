from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, VendorProfile, UserProfile, QuickService, Job, Bid, Subscription

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VendorProfile)
admin.site.register(UserProfile)
admin.site.register(QuickService)
admin.site.register(Job)
admin.site.register(Bid)
admin.site.register(Subscription)
