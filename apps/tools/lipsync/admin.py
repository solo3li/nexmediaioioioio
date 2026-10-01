from django.contrib import admin
from .models import LipSyncModelConfig, LipSyncSetting


@admin.register(LipSyncModelConfig)
class LipSyncModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_second', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(LipSyncSetting)
class LipSyncSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_video_size_mb', 'max_audio_size_mb', 'max_duration_seconds')
