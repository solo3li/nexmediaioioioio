from django.contrib import admin
from .models import AvatarVideoModelConfig, AvatarVideoSetting


@admin.register(AvatarVideoModelConfig)
class AvatarVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_second', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(AvatarVideoSetting)
class AvatarVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_audio_duration_seconds')
