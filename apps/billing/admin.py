from django.contrib import admin
from .models import Plan, Subscription, Payment, Invoice, ManualPaymentMethod, PaymentGatewayConfig


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_usd', 'price_egp', 'standard_credits', 'premium_credits', 'duration_days', 'is_free_trial', 'is_default_registration_plan', 'is_deleted')
    list_filter = ('is_free_trial', 'is_default_registration_plan', 'is_deleted')
    search_fields = ('name', 'name_ar')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email', 'plan__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'method', 'status', 'payment_id', 'created_at')
    list_filter = ('status', 'currency', 'method')
    search_fields = ('user__username', 'user__email', 'payment_id')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'total', 'currency', 'created_at')
    search_fields = ('invoice_number', 'user__username', 'user__email')


@admin.register(ManualPaymentMethod)
class ManualPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'is_active')
    list_filter = ('is_active',)
