from decimal import Decimal
from django.db import models


class ImageToVideoModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Kling')
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    cost_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='both')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Image To Video Model Config'
        verbose_name_plural = 'Image To Video Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"


class ImageToVideoSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_image_size_mb = models.IntegerField(default=20)

    class Meta:
        verbose_name = 'Image To Video General Setting'
        verbose_name_plural = 'Image To Video General Settings'

    def __str__(self):
        return f"I2V Settings (Enabled: {self.is_enabled})"
