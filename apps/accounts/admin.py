from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ApplicationUser, DeviceFingerprint, UserPhoneNumber


@admin.register(ApplicationUser)
class ApplicationUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'standard_credits', 'premium_credits', 'is_verified', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'is_superadmin', 'country')
    search_fields = ('username', 'email', 'full_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile & Details', {'fields': ('full_name', 'country', 'is_verified', 'image_url', 'visible_admin_sections')}),
        ('Credits Wallet', {'fields': ('standard_credits', 'premium_credits')}),
    )


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = ('fingerprint_hash', 'user', 'ip_address', 'created_at')
    search_fields = ('fingerprint_hash', 'ip_address', 'user__username')


@admin.register(UserPhoneNumber)
class UserPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'is_verified', 'terms_accepted_at', 'created_at')
    search_fields = ('phone_number', 'user__username')
