from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError


class ReferenceToVideoModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('both', 'Both'),
    ]

    DURATION_TYPE_CHOICES = [
        ('discrete', 'مدد محددة (Discrete)'),
        ('range', 'نطاق مرن (Range)'),
    ]

    PRICING_TYPE_CHOICES = [
        ('per_second', 'بالثانية (Per Second)'),
        ('per_request', 'بالعملية/الريكوست (Per Request)'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم النموذج")
    model_id = models.CharField(max_length=100, unique=True, verbose_name="معرف النموذج (Model ID)")
    provider = models.CharField(max_length=50, default='Crun AI', verbose_name="المزود")

    # Multimodal Reference Capabilities (Locked)
    accepts_image_ref = models.BooleanField(
        default=True, 
        verbose_name="دعم مراجع الصور (Image Reference)",
        help_text="يدعم رفع صور للشخصية أو النمط أو الزي."
    )
    max_image_refs = models.IntegerField(
        default=3, 
        verbose_name="الحد الأقصى لصور المراجع"
    )

    accepts_video_ref = models.BooleanField(
        default=False, 
        verbose_name="دعم فيديو الحركة المرجعي (Video / Motion Reference)",
        help_text="يدعم رفع مقطع فيديو لاستخراج ونقل الحركة وتوجيه الكاميرا."
    )
    max_video_refs = models.IntegerField(
        default=1, 
        verbose_name="الحد الأقصى لمقاطع الفيديو المرجعية"
    )

    accepts_audio_ref = models.BooleanField(
        default=False, 
        verbose_name="دعم الصوت المرجعي (Audio Reference / Sync)",
        help_text="يدعم رفع مسار صوتي أو موسيقي لمزامنة المشهد وتوقيت الحركة معه."
    )
    max_audio_refs = models.IntegerField(
        default=1, 
        verbose_name="الحد الأقصى للملفات الصوتية المرجعية"
    )

    # Duration Configuration (Locked)
    duration_type = models.CharField(
        max_length=20, 
        choices=DURATION_TYPE_CHOICES, 
        default='discrete', 
        verbose_name="نوع المدة الزمنية"
    )
    allowed_durations = models.CharField(
        max_length=100, 
        default='5,10', 
        help_text="المدد المسموحة مفصولة بفاصلة (مثال: 5,10) أو نطاق مرن (مثال: 4-15)", 
        verbose_name="المدد الزمنية المتاحة (ثوانٍ)"
    )
    default_duration = models.IntegerField(default=5, verbose_name="المدة الافتراضية (ثوانٍ)")

    # Resolution Configuration (Locked)
    supported_resolutions = models.CharField(
        max_length=100, 
        default='720p,1080p', 
        help_text="الجودات المدعومة مفصولة بفاصلة مثل: 480p,720p,1080p,4k", 
        verbose_name="الجودات المدعومة"
    )

    # Pricing Configuration (Editable by Admin)
    pricing_type = models.CharField(
        max_length=20, 
        choices=PRICING_TYPE_CHOICES, 
        default='per_second', 
        verbose_name="طريقة التسعير"
    )
    cost_480p = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('4.00'), 
        verbose_name="سعر 480p",
        help_text="الكريديت المطلوب لكل ثانية أو للعملية الواحدة لدقة 480p"
    )
    cost_720p = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('8.00'), 
        verbose_name="سعر 720p",
        help_text="الكريديت المطلوب لكل ثانية أو للعملية الواحدة لدقة 720p"
    )
    cost_1080p = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('12.00'), 
        verbose_name="سعر 1080p",
        help_text="الكريديت المطلوب لكل ثانية أو للعملية الواحدة لدقة 1080p"
    )
    cost_4k = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('20.00'), 
        verbose_name="سعر 4K",
        help_text="الكريديت المطلوب لكل ثانية أو للعملية الواحدة لدقة 4K"
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
        verbose_name = 'نموذج الفيديو المرجعي (R2V Model)'
        verbose_name_plural = 'نماذج الفيديو المرجعي (R2V Models)'
        ordering = ['sort_order', '-is_default', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.pk:
            orig = ReferenceToVideoModelConfig.objects.filter(pk=self.pk).values(
                'name', 'model_id', 'provider', 'duration_type', 'allowed_durations', 
                'supported_resolutions', 'accepts_image_ref', 'max_image_refs',
                'accepts_video_ref', 'max_video_refs', 'accepts_audio_ref', 'max_audio_refs'
            ).first()
            if orig:
                if (self.name != orig['name'] or 
                    self.model_id != orig['model_id'] or 
                    self.provider != orig['provider'] or
                    self.duration_type != orig['duration_type'] or
                    self.allowed_durations != orig['allowed_durations'] or
                    self.supported_resolutions != orig['supported_resolutions'] or
                    self.accepts_image_ref != orig['accepts_image_ref'] or
                    self.max_image_refs != orig['max_image_refs'] or
                    self.accepts_video_ref != orig['accepts_video_ref'] or
                    self.max_video_refs != orig['max_video_refs'] or
                    self.accepts_audio_ref != orig['accepts_audio_ref'] or
                    self.max_audio_refs != orig['max_audio_refs']):
                    raise ValidationError("اسم النموذج والمعرفات التقنية ووسائط المراجع المدعومة ثابتة ومحمية بالنظام ولا يمكن تعديلها. يمكنك فقط تعديل أسعار الجودات، نوع المحفظة، وحالة التفعيل.")

    def save(self, *args, **kwargs):
        if self.pk:
            orig = ReferenceToVideoModelConfig.objects.filter(pk=self.pk).values(
                'name', 'model_id', 'provider', 'duration_type', 'allowed_durations', 
                'supported_resolutions', 'accepts_image_ref', 'max_image_refs',
                'accepts_video_ref', 'max_video_refs', 'accepts_audio_ref', 'max_audio_refs'
            ).first()
            if orig:
                self.name = orig['name']
                self.model_id = orig['model_id']
                self.provider = orig['provider']
                self.duration_type = orig['duration_type']
                self.allowed_durations = orig['allowed_durations']
                self.supported_resolutions = orig['supported_resolutions']
                self.accepts_image_ref = orig['accepts_image_ref']
                self.max_image_refs = orig['max_image_refs']
                self.accepts_video_ref = orig['accepts_video_ref']
                self.max_video_refs = orig['max_video_refs']
                self.accepts_audio_ref = orig['accepts_audio_ref']
                self.max_audio_refs = orig['max_audio_refs']
        super().save(*args, **kwargs)

    def get_resolutions_list(self):
        """Returns list of clean lowercase resolution strings, e.g. ['480p', '720p', '1080p', '4k']"""
        if not self.supported_resolutions:
            return ['720p', '1080p']
        return [r.strip().lower() for r in self.supported_resolutions.split(',') if r.strip()]

    def get_durations_list(self):
        """Returns list of integers for discrete durations, or min/max dict for range"""
        if self.duration_type == 'discrete':
            try:
                return [int(d.strip()) for d in self.allowed_durations.split(',') if d.strip().isdigit()]
            except Exception:
                return [5, 10]
        else:
            parts = self.allowed_durations.split('-')
            try:
                return {'min': int(parts[0].strip()), 'max': int(parts[1].strip())}
            except Exception:
                return {'min': 4, 'max': 15}


class ReferenceToVideoSetting(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name="تفعيل الأداة عموماً")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    max_reference_images = models.IntegerField(default=20, verbose_name="الحد الأقصى للصور المرجعية")
    max_file_size_mb = models.IntegerField(default=50, verbose_name="الحد الأقصى لحجم الملفات المرفوعة (MB)")

    class Meta:
        verbose_name = 'إعدادات عامة للفيديو المرجعي'
        verbose_name_plural = 'إعدادات عامة للفيديو المرجعي'

    def __str__(self):
        return f"إعدادات الفيديو المرجعي (مفعلة: {self.is_enabled})"
