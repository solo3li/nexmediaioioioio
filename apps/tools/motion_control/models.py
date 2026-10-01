from decimal import Decimal
from django.db import models


class MotionControlModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Kling')
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('20.00'), help_text="Flat cost per generation")
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='both')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Motion Control Model Config'
        verbose_name_plural = 'Motion Control Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"


class MotionControlSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Motion Control General Setting'
        verbose_name_plural = 'Motion Control General Settings'

    def __str__(self):
        return f"Motion Control Settings (Enabled: {self.is_enabled})"
