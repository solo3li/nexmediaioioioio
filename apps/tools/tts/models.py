from decimal import Decimal
from django.db import models


class TtsModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default='Gemini')
    cost_per_char = models.DecimalField(max_digits=10, decimal_places=5, default=Decimal('0.00100'))
    allowed_wallet = models.CharField(max_length=20, choices=WALLET_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'TTS Model Config'
        verbose_name_plural = 'TTS Model Configs'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider}) - {self.cost_per_char}/char"


class TtsVoice(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    voice_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    display_name_ar = models.CharField(max_length=100)
    language_code = models.CharField(max_length=20, default='ar-XA')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Male')
    provider = models.CharField(max_length=50, default='Gemini')
    preview_audio_url = models.URLField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'TTS Voice'
        verbose_name_plural = 'TTS Voices'
        ordering = ['language_code', 'display_name']

    def __str__(self):
        return f"{self.display_name} ({self.language_code}) - {self.gender}"


class TtsSetting(models.Model):
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    max_chars = models.IntegerField(default=5000)

    class Meta:
        verbose_name = 'TTS General Setting'
        verbose_name_plural = 'TTS General Settings'

    def __str__(self):
        return f"TTS Settings (Enabled: {self.is_enabled})"
