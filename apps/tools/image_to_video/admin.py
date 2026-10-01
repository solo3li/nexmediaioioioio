from django.contrib import admin
from .models import ImageToVideoModelConfig, ImageToVideoSetting


@admin.register(ImageToVideoModelConfig)
class ImageToVideoModelConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'image_input_type',
        'max_input_images',
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
    list_filter = ('is_active', 'image_input_type', 'max_input_images', 'pricing_type', 'allowed_wallet', 'duration_type')
    search_fields = ('name', 'model_id')

    # قفل اسم النموذج ومعرفاته التقنية لتكون للقراءة فقط ومنع تغييرها من الأدمن نهائياً
    readonly_fields = (
        'name', 
        'model_id', 
        'provider', 
        'image_input_type',
        'max_input_images',
        'accepts_end_frame',
        'duration_type', 
        'allowed_durations', 
        'supported_resolutions',
        'default_duration'
    )

    fieldsets = (
        ('بيانات النموذج الأساسية وسعة الصور (ثابتة ومحمية من النظام)', {
            'fields': ('name', 'model_id', 'provider', 'image_input_type', 'max_input_images', 'accepts_end_frame', 'supported_resolutions', 'duration_type', 'allowed_durations', 'default_duration'),
            'description': 'اسم النموذج والمعرفات التقنية وعدد الصور مقفلة لحماية مسار التوليد والتكامل مع Crun AI.'
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
        # منع إضافة نماذج عشوائية غير معتمدة
        return False

    def has_delete_permission(self, request, obj=None):
        # منع حذف النماذج الأساسية
        return False


@admin.register(ImageToVideoSetting)
class ImageToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'maintenance_mode', 'max_image_size_mb')
