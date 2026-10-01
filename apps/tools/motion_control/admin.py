from django.contrib import admin
from .models import MotionControlModelConfig, MotionControlSetting


@admin.register(MotionControlModelConfig)
class MotionControlModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active',
        'is_default',
        'cost_480p',
        'cost_720p',
        'cost_1080p',
        'cost_4k',
        'pricing_type',
        'allowed_wallet',
        'sort_order',
    )
    list_editable = (
        'is_active',
        'is_default',
        'cost_480p',
        'cost_720p',
        'cost_1080p',
        'cost_4k',
        'allowed_wallet',
        'sort_order',
    )
    list_filter = ('is_active', 'is_default', 'allowed_wallet', 'pricing_type')
    search_fields = ('name', 'model_id')

    readonly_fields = (
        'name',
        'model_id',
        'provider',
        'pricing_type',
        'supported_resolutions',
        'min_duration',
        'max_duration',
        'allowed_durations',
    )

    fieldsets = (
        ('المواصفات الفنية للنموذج (محمية ومقفلة تقنياً)', {
            'fields': (
                'name',
                'model_id',
                'provider',
                'pricing_type',
                'supported_resolutions',
                ('min_duration', 'max_duration'),
                'allowed_durations',
            ),
            'description': 'اسم النموذج والمعرفات التقنية مقفلة لحماية مسار التوليد والتكامل مع Crun AI.'
        }),
        ('تسعير الجودات التفاعلي (قابل للتعديل)', {
            'fields': (
                ('cost_480p', 'cost_720p'),
                ('cost_1080p', 'cost_4k'),
                'cost_per_second',
                'base_cost',
            ),
            'description': 'حدد تكلفة النقاط لكل ثانية (أو التكلفة المقطوعة) لكل دقة يدعمها النموذج.'
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


@admin.register(MotionControlSetting)
class MotionControlSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_enabled', 'maintenance_mode')
    list_editable = ('is_enabled', 'maintenance_mode')
