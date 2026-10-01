from decimal import Decimal
from django.db import models


class LipSyncModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Vidu')
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.50'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Lip Sync Model Config'
        verbose_name_plural = 'Lip Sync Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"


class LipSyncSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_video_size_mb = models.IntegerField(default=100)
    max_audio_size_mb = models.IntegerField(default=25)
    max_duration_seconds = models.IntegerField(default=120)

    class Meta:
        verbose_name = 'Lip Sync General Setting'
        verbose_name_plural = 'Lip Sync General Settings'

    def __str__(self):
        return f"LipSync Settings (Enabled: {self.is_enabled})"
