from django.contrib import admin
from .models import SttModelConfig, SttSetting


@admin.register(SttModelConfig)
class SttModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_second', 'cost_per_minute', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(SttSetting)
class SttSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_file_size_mb', 'max_duration_minutes')
