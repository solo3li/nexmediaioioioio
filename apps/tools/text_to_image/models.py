from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError


class TextToImageModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم النموذج")
    model_id = models.CharField(max_length=100, unique=True, verbose_name="معرف النموذج (Model ID)")
    provider = models.CharField(max_length=50, default='Crun AI', verbose_name="المزود")

    # Resolution Configuration (Locked)
    supported_resolutions = models.CharField(
        max_length=100,
        default='1k,2k,4k',
        help_text="الجودات المدعومة مفصولة بفاصلة مثل: 1k,2k,4k",
        verbose_name="الجودات المدعومة"
    )

    # Resolution Pricing (Editable by Admin)
    cost_1k = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('2.00'),
        verbose_name="سعر دقة 1K (Standard)",
        help_text="الكريديت المطلوب لتوليد صورة واحدة بدقة 1K (1024px)"
    )
    cost_2k = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('4.00'),
        verbose_name="سعر دقة 2K (HD)",
        help_text="الكريديت المطلوب لتوليد صورة واحدة بدقة 2K (2048px)"
    )
    cost_4k = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('8.00'),
        verbose_name="سعر دقة 4K (Ultra)",
        help_text="الكريديت المطلوب لتوليد صورة واحدة بدقة 4K (4096px)"
    )

    allowed_wallet = models.CharField(
        max_length=20,
        choices=WALLET_CHOICES,
        default='both',
        verbose_name="المحفظة المسموحة"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل للاستخدام")
    is_default = models.BooleanField(default=False, verbose_name="النموذج الافتراضي")
    sort_order = models.IntegerField(default=0, verbose_name="ترتيب العرض")

    class Meta:
        verbose_name = 'نموذج تحويل النص إلى صور (T2I Model)'
        verbose_name_plural = 'نماذج تحويل النص إلى صور (T2I Models)'
        ordering = ['sort_order', '-is_default', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.pk:
            orig = TextToImageModelConfig.objects.filter(pk=self.pk).values(
                'name', 'model_id', 'provider', 'supported_resolutions'
            ).first()
            if orig:
                if (self.name != orig['name'] or 
                    self.model_id != orig['model_id'] or 
                    self.provider != orig['provider'] or
                    self.supported_resolutions != orig['supported_resolutions']):
                    raise ValidationError("اسم النموذج والمعرفات التقنية والجودات المدعومة ثابتة ومحمية بالنظام ولا يمكن تعديلها. يمكنك فقط تعديل أسعار الجودات، نوع المحفظة، وحالة التفعيل.")

    def save(self, *args, **kwargs):
        if self.pk:
            orig = TextToImageModelConfig.objects.filter(pk=self.pk).values(
                'name', 'model_id', 'provider', 'supported_resolutions'
            ).first()
            if orig:
                self.name = orig['name']
                self.model_id = orig['model_id']
                self.provider = orig['provider']
                self.supported_resolutions = orig['supported_resolutions']
        super().save(*args, **kwargs)

    def get_resolutions_list(self):
        """Returns list of clean lowercase resolution strings, e.g. ['1k', '2k', '4k']"""
        if not self.supported_resolutions:
            return ['1k', '2k', '4k']
        return [r.strip().lower() for r in self.supported_resolutions.split(',') if r.strip()]

    def get_cost_for_resolution(self, res):
        """Returns the cost for a given resolution string"""
        res = (res or '1k').lower().strip()
        if res == '4k':
            return self.cost_4k
        elif res == '2k':
            return self.cost_2k
        else:
            return self.cost_1k


class TextToImageSetting(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name="تفعيل الأداة عموماً")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    max_prompt_length = models.IntegerField(default=1000, verbose_name="الحد الأقصى لطول الوصف (Prompt)")

    class Meta:
        verbose_name = 'إعدادات عامة لتحويل النص إلى صور'
        verbose_name_plural = 'إعدادات عامة لتحويل النص إلى صور'

    def __str__(self):
        return f"إعدادات أداة توليد الصور (مفعلة: {self.is_enabled})"
