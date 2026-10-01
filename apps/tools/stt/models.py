from decimal import Decimal
from django.db import models


class SttModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Whisper')
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0167'))
    cost_per_minute = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'STT Model Config'
        verbose_name_plural = 'STT Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider}) - {self.cost_per_minute}/min"


class SttSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_file_size_mb = models.IntegerField(default=25)
    max_duration_minutes = models.IntegerField(default=10)

    class Meta:
        verbose_name = 'STT General Setting'
        verbose_name_plural = 'STT General Settings'

    def __str__(self):
        return f"STT Settings (Enabled: {self.is_enabled})"
