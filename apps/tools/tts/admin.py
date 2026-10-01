from django.contrib import admin
from .models import TtsModelConfig, TtsVoice, TtsSetting


@admin.register(TtsModelConfig)
class TtsModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'provider', 'cost_per_char', 'allowed_wallet', 'is_default', 'is_active')
    list_filter = ('provider', 'allowed_wallet', 'is_active')
    search_fields = ('name', 'model_id', 'provider')


@admin.register(TtsVoice)
class TtsVoiceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'voice_id', 'language_code', 'gender', 'provider', 'is_active')
    list_filter = ('language_code', 'gender', 'provider', 'is_active')
    search_fields = ('display_name', 'display_name_ar', 'voice_id')


@admin.register(TtsSetting)
class TtsSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_chars')
