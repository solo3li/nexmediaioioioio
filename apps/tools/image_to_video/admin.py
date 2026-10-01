from django.contrib import admin
from .models import ImageToVideoModelConfig, ImageToVideoSetting


@admin.register(ImageToVideoModelConfig)
class ImageToVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_second', 'cost_fixed', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(ImageToVideoSetting)
class ImageToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_image_size_mb')
