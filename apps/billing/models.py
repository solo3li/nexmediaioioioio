from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """Subscription plan with tool access permissions and credit quotas."""
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    description_ar = models.TextField(blank=True, null=True)

    # Features listed line-by-line
    features = models.TextField(blank=True, null=True)
    features_ar = models.TextField(blank=True, null=True)

    duration_days = models.IntegerField(default=30)
    grace_period_days = models.IntegerField(default=3)

    # Multi-currency pricing
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_percentage_usd = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tax_percentage_egp = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    fixed_fee_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fixed_fee_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Credits economy
    standard_credits = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0.0000'))
    premium_credits = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0.0000'))

    # AI Tools Access Permissions
    text_to_image_enabled = models.BooleanField(default=True)
    text_to_video_enabled = models.BooleanField(default=True)
    image_to_video_enabled = models.BooleanField(default=True)
    reference_to_video_enabled = models.BooleanField(default=True)
    lipsync_enabled = models.BooleanField(default=True)
    motion_control_enabled = models.BooleanField(default=True)
    stt_enabled = models.BooleanField(default=True)
    tts_enabled = models.BooleanField(default=True)
    avatar_video_enabled = models.BooleanField(default=True)

    is_free_trial = models.BooleanField(default=False)
    allowed_voices = models.TextField(blank=True, null=True, help_text="Comma-separated voice names")
    is_default_registration_plan = models.BooleanField(default=False)

    # Affiliate Commission Settings
    affiliate_first_commission_type = models.CharField(max_length=50, default="Percentage")
    affiliate_first_commission_value_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    affiliate_first_commission_value_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    affiliate_recurring_commission_type = models.CharField(max_length=50, default="Percentage")
    affiliate_recurring_commission_value_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    affiliate_recurring_commission_value_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['price_usd', 'id']

    def __str__(self):
        return f"{self.name} (${self.price_usd})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('freeze', 'Freeze'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscriptions')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status})"

    @property
    def is_currently_active(self):
        return self.status == 'active' and self.end_date >= timezone.now()


class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_id = models.CharField(max_length=255, blank=True, null=True, help_text="External Transaction ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    method = models.CharField(max_length=50, help_text="paymob, paypal, manual, admin_grant")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    receipt_url = models.URLField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.status})"


class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    invoice_number = models.CharField(max_length=100, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    pdf_url = models.URLField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.total} {self.currency}"


class ManualPaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    account_details = models.TextField(help_text="Bank Account, IBAN, InstaPay, Vodafone Cash, etc.")
    instructions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Manual Payment Method'
        verbose_name_plural = 'Manual Payment Methods'

    def __str__(self):
        return self.name


class PaymentGatewayConfig(models.Model):
    provider = models.CharField(max_length=50, unique=True, help_text="paymob, paypal")
    public_key = models.CharField(max_length=500, blank=True, null=True)
    secret_key = models.CharField(max_length=500, blank=True, null=True)
    extra_config = models.JSONField(default=dict, blank=True, help_text="Additional JSON options")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Payment Gateway Config'
        verbose_name_plural = 'Payment Gateway Configs'

    def __str__(self):
        return f"{self.provider} ({'Active' if self.is_active else 'Inactive'})"
