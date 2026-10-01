from django.contrib import admin
from .models import TextToImageModelConfig, TextToImageSetting


@admin.register(TextToImageModelConfig)
class TextToImageModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_image', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(TextToImageSetting)
class TextToImageSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode')
