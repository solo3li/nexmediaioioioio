from django.contrib import admin
from .models import TextToVideoModelConfig, TextToVideoSetting


@admin.register(TextToVideoModelConfig)
class TextToVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'pricing_type', 
        'cost_480p', 
        'cost_720p', 
        'cost_1080p', 
        'cost_4k', 
        'supported_resolutions', 
        'allowed_durations', 
        'is_active', 
        'is_default'
    )
    list_editable = (
        'pricing_type',
        'cost_480p', 
        'cost_720p', 
        'cost_1080p', 
        'cost_4k', 
        'is_active'
    )
    list_filter = ('is_active', 'pricing_type', 'allowed_wallet', 'duration_type')
    search_fields = ('name', 'model_id')

    # قفل اسم النموذج ومعرفاته التقنية لتكون للقراءة فقط ومنع تغييرها من الأدمن نهائياً
    readonly_fields = (
        'name', 
        'model_id', 
        'provider', 
        'duration_type', 
        'allowed_durations', 
        'supported_resolutions',
        'default_duration'
    )

    fieldsets = (
        ('بيانات النموذج الأساسية (ثابتة ومحمية من النظام)', {
            'fields': ('name', 'model_id', 'provider', 'supported_resolutions', 'duration_type', 'allowed_durations', 'default_duration'),
            'description': 'اسم النموذج والمعرفات التقنية مقفلة لحماية مسار التوليد والتكامل مع Crun AI.'
        }),
        ('إعدادات التسعير والكريديت (متاح للأدمن تعديلها بحرية)', {
            'fields': ('pricing_type', 'cost_480p', 'cost_720p', 'cost_1080p', 'cost_4k', 'allowed_wallet'),
            'description': 'تحكم في طريقة التسعير (بالثانية أو بالعملية الثابتة) وسعر كل دقة بالكريديت.'
        }),
        ('حالة التفعيل والظهور في الاستوديو', {
            'fields': ('is_active', 'is_default', 'sort_order'),
        }),
    )

    def has_add_permission(self, request):
        # منع إضافة نماذج عشوائية غير معتمدة؛ النماذج الـ 19 الرسمية مسجلة ومثبتة مسبقاً
        return False

    def has_delete_permission(self, request, obj=None):
        # منع حذف النماذج الأساسية؛ يمكن فقط تعطيلها عبر is_active
        return False


@admin.register(TextToVideoSetting)
class TextToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_prompt_length')
