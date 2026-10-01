from django.contrib import admin
from .models import ReferenceToVideoModelConfig, ReferenceToVideoSetting


@admin.register(ReferenceToVideoModelConfig)
class ReferenceToVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_generation', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(ReferenceToVideoSetting)
class ReferenceToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_reference_images')
