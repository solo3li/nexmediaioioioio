from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone


class ApplicationUser(AbstractUser):
    """
    Core user model replicating NexClone ApplicationUser
    with Dual-Wallet system (Standard & Premium Credits).
    """
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    last_verification_email_sent_at = models.DateTimeField(null=True, blank=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    is_superadmin = models.BooleanField(default=False)
    visible_admin_sections = models.TextField(blank=True, null=True, help_text="Comma-separated admin sections")

    # Dual-Wallet Economy
    standard_credits = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Standard Credits Balance"
    )
    premium_credits = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Premium Credits Balance"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Application User'
        verbose_name_plural = 'Application Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.username or self.email or str(self.id)

    @property
    def total_credits(self):
        return self.standard_credits + self.premium_credits

    def has_sufficient_balance(self, standard_cost: Decimal = Decimal('0.0'), premium_cost: Decimal = Decimal('0.0')) -> bool:
        return self.standard_credits >= standard_cost and self.premium_credits >= premium_cost

    @transaction.atomic
    def deduct_credits(self, standard_cost: Decimal = Decimal('0.0'), premium_cost: Decimal = Decimal('0.0')) -> bool:
        """Deduct credits atomically using select_for_update."""
        user = ApplicationUser.objects.select_for_update().get(id=self.id)
        if user.standard_credits < standard_cost or user.premium_credits < premium_cost:
            return False
        user.standard_credits -= standard_cost
        user.premium_credits -= premium_cost
        user.save(update_fields=['standard_credits', 'premium_credits'])
        self.standard_credits = user.standard_credits
        self.premium_credits = user.premium_credits
        return True

    @transaction.atomic
    def add_credits(self, standard_amount: Decimal = Decimal('0.0'), premium_amount: Decimal = Decimal('0.0')) -> None:
        """Add credits atomically to user wallets."""
        user = ApplicationUser.objects.select_for_update().get(id=self.id)
        user.standard_credits += standard_amount
        user.premium_credits += premium_amount
        user.save(update_fields=['standard_credits', 'premium_credits'])
        self.standard_credits = user.standard_credits
        self.premium_credits = user.premium_credits


class DeviceFingerprint(models.Model):
    """Prevents free-trial abuse and tracks user login hardware signatures."""
    user = models.ForeignKey(ApplicationUser, on_delete=models.CASCADE, related_name='fingerprints', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    fingerprint_hash = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Device Fingerprint'
        verbose_name_plural = 'Device Fingerprints'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fingerprint_hash[:16]} ({self.user})"


class UserPhoneNumber(models.Model):
    """User phone verification and terms tracking."""
    user = models.OneToOneField(ApplicationUser, on_delete=models.CASCADE, related_name='phone_details')
    phone_number = models.CharField(max_length=32, unique=True)
    is_verified = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Phone Number'
        verbose_name_plural = 'User Phone Numbers'

    def __str__(self):
        return f"{self.phone_number} ({self.user.username})"
