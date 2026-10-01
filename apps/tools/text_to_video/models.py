from decimal import Decimal
from django.db import models


class TextToVideoModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Kling')
    cost_480p = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.40'), help_text="Credits per sec (480p)")
    cost_720p = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'), help_text="Credits per sec (720p)")
    cost_1080p = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('8.00'), help_text="Credits per sec (1080p)")
    cost_4k = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('15.00'), help_text="Credits per sec (4K)")
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='both')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Text To Video Model Config'
        verbose_name_plural = 'Text To Video Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"


class TextToVideoSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_prompt_length = models.IntegerField(default=1000)

    class Meta:
        verbose_name = 'Text To Video General Setting'
        verbose_name_plural = 'Text To Video General Settings'

    def __str__(self):
        return f"T2V Settings (Enabled: {self.is_enabled})"
