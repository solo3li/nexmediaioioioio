from django.contrib import admin
from .models import TextToImageModelConfig, TextToImageSetting


@admin.register(TextToImageModelConfig)
class TextToImageModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost_1k',
        'cost_2k',
        'cost_4k',
        'supported_resolutions',
        'allowed_wallet',
        'is_active',
        'is_default'
    )
    list_editable = (
        'cost_1k',
        'cost_2k',
        'cost_4k',
        'is_active'
    )
    list_filter = ('is_active', 'allowed_wallet')
    search_fields = ('name', 'model_id')

    # قفل اسم النموذج ومعرفاته التقنية لتكون للقراءة فقط ومنع تغييرها من الأدمن نهائياً
    readonly_fields = (
        'name',
        'model_id',
        'provider',
        'supported_resolutions'
    )

    fieldsets = (
        ('بيانات النموذج الأساسية والجودات (ثابتة ومحمية من النظام)', {
            'fields': ('name', 'model_id', 'provider', 'supported_resolutions'),
            'description': 'اسم النموذج والمعرفات التقنية مقفلة لحماية مسار التوليد والتكامل مع Crun AI.'
        }),
        ('إعدادات التسعير والكريديت (متاح للأدمن تعديلها بحرية)', {
            'fields': ('cost_1k', 'cost_2k', 'cost_4k', 'allowed_wallet'),
            'description': 'تحكم في سعر كل دقة (1K Standard, 2K HD, 4K Ultra) بالكريديت للصورة الواحدة.'
        }),
        ('حالة التفعيل والظهور في الاستوديو', {
            'fields': ('is_active', 'is_default', 'sort_order'),
        }),
    )

    def has_add_permission(self, request):
        # منع إضافة نماذج عشوائية غير معتمدة
        return False

    def has_delete_permission(self, request, obj=None):
        # منع حذف النماذج الأساسية
        return False


@admin.register(TextToImageSetting)
class TextToImageSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_prompt_length')
