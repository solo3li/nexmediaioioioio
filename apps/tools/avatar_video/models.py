from decimal import Decimal
from django.db import models


class AvatarVideoModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Hedra')
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='both')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Avatar To Video Model Config'
        verbose_name_plural = 'Avatar To Video Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"


class AvatarVideoSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_audio_duration_seconds = models.IntegerField(default=120)

    class Meta:
        verbose_name = 'Avatar To Video General Setting'
        verbose_name_plural = 'Avatar To Video General Settings'

    def __str__(self):
        return f"Avatar Video Settings (Enabled: {self.is_enabled})"
