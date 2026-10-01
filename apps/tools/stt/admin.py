from django.contrib import admin
from .models import SttModelConfig, SttSetting


@admin.register(SttModelConfig)
class SttModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active',
        'is_default',
        'cost_per_minute',
        'cost_per_second',
        'pricing_type',
        'allowed_wallet',
        'sort_order',
    )
    list_editable = (
        'is_active',
        'is_default',
        'cost_per_minute',
        'cost_per_second',
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
        'min_duration_seconds',
        'max_duration_seconds',
    )

    fieldsets = (
        ('المواصفات الفنية للنموذج (محمية ومقفلة تقنياً)', {
            'fields': (
                'name',
                'model_id',
                'provider',
                'pricing_type',
                ('min_duration_seconds', 'max_duration_seconds'),
            ),
            'description': 'اسم النموذج والمعرفات التقنية مقفلة لحماية مسار التوليد والتكامل مع OpenAI Whisper.'
        }),
        ('تسعير التفريغ الصوتي (قابل للتعديل)', {
            'fields': (
                'cost_per_minute',
                'cost_per_second',
            ),
            'description': 'حدد تكلفة النقاط لكل دقيقة كاملة لتفريغ الصوت بدقة الثواني.'
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


@admin.register(SttSetting)
class SttSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_enabled', 'maintenance_mode', 'max_file_size_mb', 'max_duration_minutes')
    list_editable = ('is_enabled', 'maintenance_mode', 'max_file_size_mb', 'max_duration_minutes')
