from django.contrib import admin
from django.utils import timezone
from .models import AffiliateSettings, AffiliateProfile, AffiliateReferral, AffiliateCommission, AffiliatePayout


@admin.register(AffiliateSettings)
class AffiliateSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_program_active', 'attribution_period_days', 'hold_period_days', 'first_purchase_rate', 'recurring_rate', 'min_payout_usd', 'min_payout_egp')

    def has_add_permission(self, request):
        return not AffiliateSettings.objects.exists()


class AffiliateCommissionInline(admin.TabularInline):
    model = AffiliateCommission
    extra = 0
    readonly_fields = ('created_at', 'available_at', 'paid_at')
    fields = ('type', 'amount', 'currency', 'rate', 'status', 'created_at', 'available_at')


class AffiliatePayoutInline(admin.TabularInline):
    model = AffiliatePayout
    extra = 0
    readonly_fields = ('requested_at', 'processed_at')
    fields = ('amount', 'currency', 'payout_method', 'status', 'requested_at', 'processed_at')


@admin.register(AffiliateProfile)
class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'user', 'referral_code', 'is_active', 'total_clicks', 'pending_usd', 'available_usd', 'pending_egp', 'available_egp', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('display_id', 'referral_code', 'user__username', 'user__email', 'mobile_number')
    inlines = [AffiliateCommissionInline, AffiliatePayoutInline]


@admin.register(AffiliateReferral)
class AffiliateReferralAdmin(admin.ModelAdmin):
    list_display = ('id', 'affiliate_profile', 'referred_user', 'has_converted', 'clicked_at', 'attribution_expires_at')
    list_filter = ('has_converted', 'clicked_at')
    search_fields = ('affiliate_profile__referral_code', 'referred_user__username', 'session_token')


@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'affiliate_profile', 'customer', 'type', 'amount', 'currency', 'rate', 'status', 'created_at', 'available_at')
    list_filter = ('status', 'type', 'currency', 'created_at')
    search_fields = ('affiliate_profile__display_id', 'affiliate_profile__referral_code', 'customer__username')
    actions = ['release_hold_to_available']

    @admin.action(description="Release Hold Period -> Mark as Available")
    def release_hold_to_available(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='AVAILABLE')
        self.message_user(request, f"Updated {count} commissions to AVAILABLE.")


@admin.register(AffiliatePayout)
class AffiliatePayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'affiliate_profile', 'amount', 'currency', 'payout_method', 'status', 'requested_at', 'processed_at')
    list_filter = ('status', 'currency', 'payout_method', 'requested_at')
    search_fields = ('affiliate_profile__display_id', 'payout_account', 'rejection_reason')
    actions = ['mark_approved', 'mark_paid']

    @admin.action(description="Approve Selected Payouts")
    def mark_approved(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='APPROVED')
        self.message_user(request, f"{count} payouts approved.")

    @admin.action(description="Mark Selected Payouts as PAID")
    def mark_paid(self, request, queryset):
        count = queryset.filter(status__in=['PENDING', 'APPROVED', 'PROCESSING']).update(
            status='PAID',
            processed_at=timezone.now()
        )
        self.message_user(request, f"{count} payouts marked as PAID.")
