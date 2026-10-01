from django.contrib import admin
from .models import TextToVideoModelConfig, TextToVideoSetting


@admin.register(TextToVideoModelConfig)
class TextToVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_480p', 'cost_720p', 'cost_1080p', 'cost_4k', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(TextToVideoSetting)
class TextToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_prompt_length')
