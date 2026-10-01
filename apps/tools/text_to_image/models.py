from decimal import Decimal
from django.db import models


class TextToImageModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Grok')
    cost_per_image = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('4.00'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Text To Image Model Config'
        verbose_name_plural = 'Text To Image Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider}) - {self.cost_per_image}/image"


class TextToImageSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Text To Image General Setting'
        verbose_name_plural = 'Text To Image General Settings'

    def __str__(self):
        return f"T2I Settings (Enabled: {self.is_enabled})"
