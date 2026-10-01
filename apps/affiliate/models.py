import uuid
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone


class AffiliateSettings(models.Model):
    """Global configuration for affiliate program"""
    attribution_period_days = models.PositiveIntegerField(default=30, help_text="Cookie / referral attribution window in days")
    hold_period_days = models.PositiveIntegerField(default=14, help_text="Days to hold commission before becoming available for withdrawal")
    first_purchase_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00'), help_text="Commission % for first purchase")
    recurring_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'), help_text="Commission % for recurring purchases")
    max_package_duration_days = models.PositiveIntegerField(default=365, help_text="Cap on cumulative subscription days eligible for commission")
    min_payout_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    min_payout_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    is_program_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Affiliate Setting'
        verbose_name_plural = 'Affiliate Settings'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Affiliate Config (1st: {self.first_purchase_rate}%, Rec: {self.recurring_rate}%, Hold: {self.hold_period_days}d)"


class AffiliateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='affiliate_profile')
    display_id = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    referral_code = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    total_clicks = models.PositiveIntegerField(default=0)
    
    # Contact & Onboarding
    mobile_number = models.CharField(max_length=30, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    facebook_account = models.CharField(max_length=200, blank=True)
    policy_accepted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Affiliate Profile'
        verbose_name_plural = 'Affiliate Profiles'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.display_id:
            # Generate display ID AF-XXXXX
            self.display_id = f"AF-{uuid.uuid4().hex[:6].upper()}"
        if not self.referral_code:
            self.referral_code = self.user.username.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_id} - {self.user.username} (Code: {self.referral_code})"

    def get_balance(self, currency: str, status: str) -> Decimal:
        val = self.commissions.filter(currency=currency.upper(), status=status.upper()).aggregate(total=Sum('amount'))['total']
        return val or Decimal('0.00')

    @property
    def pending_usd(self) -> Decimal:
        return self.get_balance('USD', 'PENDING')

    @property
    def available_usd(self) -> Decimal:
        paid_payouts = self.payouts.filter(currency='USD', status__in=['APPROVED', 'PROCESSING', 'PAID']).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        earned_available = self.get_balance('USD', 'AVAILABLE')
        return max(Decimal('0.00'), earned_available - paid_payouts)

    @property
    def pending_egp(self) -> Decimal:
        return self.get_balance('EGP', 'PENDING')

    @property
    def available_egp(self) -> Decimal:
        paid_payouts = self.payouts.filter(currency='EGP', status__in=['APPROVED', 'PROCESSING', 'PAID']).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        earned_available = self.get_balance('EGP', 'AVAILABLE')
        return max(Decimal('0.00'), earned_available - paid_payouts)


class AffiliateReferral(models.Model):
    affiliate_profile = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='referrals')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_by_records')
    session_token = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    clicked_at = models.DateTimeField(default=timezone.now)
    attribution_expires_at = models.DateTimeField()
    has_converted = models.BooleanField(default=False)
    first_eligible_payment_at = models.DateTimeField(null=True, blank=True)
    accumulated_package_days = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Affiliate Referral'
        verbose_name_plural = 'Affiliate Referrals'
        ordering = ['-clicked_at']

    def save(self, *args, **kwargs):
        if not self.attribution_expires_at:
            settings_obj = AffiliateSettings.get_settings()
            self.attribution_expires_at = timezone.now() + timedelta(days=settings_obj.attribution_period_days)
        super().save(*args, **kwargs)

    @property
    def is_attribution_active(self) -> bool:
        return timezone.now() <= self.attribution_expires_at

    def __str__(self):
        user_label = self.referred_user.username if self.referred_user else f"Visitor ({self.session_token[:8]}...)" if self.session_token else "Anonymous"
        return f"Referral by {self.affiliate_profile.display_id} -> {user_label}"


class AffiliateCommission(models.Model):
    TYPE_CHOICES = [
        ('FIRST_PURCHASE', 'First Purchase'),
        ('RECURRING', 'Recurring'),
        ('REVERSAL', 'Reversal'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending (Hold Period)'),
        ('AVAILABLE', 'Available for Payout'),
        ('CANCELLED', 'Cancelled'),
        ('REVERSED', 'Reversed (Refunded)'),
        ('PAID', 'Paid Out'),
    ]

    affiliate_profile = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='commissions')
    referral = models.ForeignKey(AffiliateReferral, on_delete=models.CASCADE, related_name='commissions')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='affiliate_commissions_generated')
    plan = models.ForeignKey('billing.Plan', on_delete=models.SET_NULL, null=True, blank=True)
    subscription = models.ForeignKey('billing.Subscription', on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey('billing.Payment', on_delete=models.SET_NULL, null=True, blank=True)

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='FIRST_PURCHASE')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Applied percentage rate")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)

    created_at = models.DateTimeField(default=timezone.now)
    available_at = models.DateTimeField(help_text="Release date after hold period")
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Affiliate Commission'
        verbose_name_plural = 'Affiliate Commissions'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.available_at:
            settings_obj = AffiliateSettings.get_settings()
            self.available_at = timezone.now() + timedelta(days=settings_obj.hold_period_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} {self.amount} {self.currency} for {self.affiliate_profile.display_id} [{self.status}]"


class AffiliatePayout(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Admin Review'),
        ('APPROVED', 'Approved'),
        ('PROCESSING', 'Processing Payment'),
        ('PAID', 'Paid & Completed'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
    ]

    affiliate_profile = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payout_method = models.CharField(max_length=100, help_text="e.g. Vodafone Cash, Instapay, Bank Transfer, PayPal")
    payout_account = models.CharField(max_length=300, help_text="Account details, phone number, IBAN or PayPal email")
    affiliate_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    rejection_reason = models.CharField(max_length=500, blank=True, null=True)
    transfer_receipt_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Receipt URL / Proof of transfer")
    requested_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Affiliate Payout'
        verbose_name_plural = 'Affiliate Payouts'
        ordering = ['-requested_at']

    def __str__(self):
        return f"Payout #{self.id}: {self.amount} {self.currency} ({self.payout_method}) - {self.affiliate_profile.display_id} [{self.status}]"
