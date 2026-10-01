from django.contrib import admin
from django.utils.html import format_html
from .models import Plan, Subscription, Payment, Invoice, ManualPaymentMethod, PaymentGatewayConfig
from .services import BillingService


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_usd', 'price_egp', 'standard_credits', 'premium_credits', 'duration_days', 'is_free_trial', 'is_default_registration_plan', 'is_deleted')
    list_filter = ('is_free_trial', 'is_default_registration_plan', 'is_deleted')
    search_fields = ('name', 'name_ar')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'plan__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount', 'currency', 'method', 'status', 'receipt_preview', 'payment_id', 'created_at')
    list_filter = ('status', 'currency', 'method', 'created_at')
    search_fields = ('user__username', 'user__email', 'payment_id')
    actions = ['approve_manual_payments']

    def receipt_preview(self, obj):
        if obj.receipt_url:
            return format_html('<a href="{}" target="_blank" style="color: #c5a059; font-weight: bold;">View Receipt</a>', obj.receipt_url)
        return "-"
    receipt_preview.short_description = "Receipt"

    @admin.action(description="Approve Selected Payments (Grant Credits & Activate)")
    def approve_manual_payments(self, request, queryset):
        success_count = 0
        for payment in queryset.filter(status='Pending'):
            try:
                BillingService.activate_subscription_and_grant_credits(payment)
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Error processing payment #{payment.id}: {e}", level='error')
        self.message_user(request, f"Successfully activated {success_count} payments, credited wallets, and updated affiliate commissions.")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'total', 'currency', 'created_at', 'pdf_link')
    search_fields = ('invoice_number', 'user__username', 'user__email')

    def pdf_link(self, obj):
        if obj.pdf_url:
            return format_html('<a href="{}" target="_blank" style="color: #c5a059;">Download PDF</a>', obj.pdf_url)
        return "-"
    pdf_link.short_description = "PDF"


@admin.register(ManualPaymentMethod)
class ManualPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'account_details')


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'is_active')
    list_filter = ('is_active',)
