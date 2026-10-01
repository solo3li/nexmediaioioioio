from django.contrib import admin
from .models import MotionControlModelConfig, MotionControlSetting


@admin.register(MotionControlModelConfig)
class MotionControlModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'base_cost', 'cost_per_second', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(MotionControlSetting)
class MotionControlSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode')
