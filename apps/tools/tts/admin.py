from django.contrib import admin
from .models import TtsModelConfig, TtsVoice, TtsSetting


@admin.register(TtsModelConfig)
class TtsModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active',
        'is_default',
        'quality_tier',
        'chars_per_block',
        'cost_per_block_standard',
        'cost_per_block_high',
        'allowed_wallet',
        'sort_order',
    )
    list_editable = (
        'is_active',
        'is_default',
        'chars_per_block',
        'cost_per_block_standard',
        'cost_per_block_high',
        'allowed_wallet',
        'sort_order',
    )
    list_filter = ('quality_tier', 'is_active', 'is_default', 'allowed_wallet')
    search_fields = ('name', 'model_id')

    readonly_fields = (
        'name',
        'model_id',
        'provider',
        'quality_tier',
    )

    fieldsets = (
        ('المواصفات الفنية للنموذج (محمية ومقفلة تقنياً)', {
            'fields': (
                'name',
                'model_id',
                'provider',
                'quality_tier',
            ),
            'description': 'اسم النموذج والمعرفات التقنية مقفلة لحماية مسار التوليد والتكامل مع Google Gemini.'
        }),
        ('تسعير البلوكات التفاعلي (قابل للتعديل)', {
            'fields': (
                'chars_per_block',
                ('cost_per_block_standard', 'cost_per_block_high'),
                'cost_per_char',
            ),
            'description': 'حدد عدد الحروف في كل بلوك وتكلفة البلوك الواحد لكل من الجودة العادية والجودة العالية.'
        }),
        ('إعدادات الإتاحة والتحكم', {
            'fields': (
                'allowed_wallet',
                ('is_active', 'is_default'),
                'sort_order',
            )
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TtsVoice)
class TtsVoiceAdmin(admin.ModelAdmin):
    list_display = (
        'display_name_ar',
        'display_name',
        'gender',
        'voice_category',
        'is_active',
        'sort_order',
    )
    list_display_links = ('display_name_ar',)
    list_editable = (
        'display_name',
        'gender',
        'voice_category',
        'is_active',
        'sort_order',
    )
    list_filter = ('gender', 'voice_category', 'is_active')
    search_fields = ('display_name_ar', 'display_name', 'voice_id', 'accent_note')

    readonly_fields = ('voice_id', 'provider')


@admin.register(TtsSetting)
class TtsSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_enabled', 'maintenance_mode', 'max_chars')
    list_editable = ('is_enabled', 'maintenance_mode', 'max_chars')
