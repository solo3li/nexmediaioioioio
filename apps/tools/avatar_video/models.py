from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models


class AvatarVideoModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'الرصيد الأساسي (Standard)'),
        ('premium', 'الرصيد المميز (Premium)'),
        ('both', 'المحفظتان معاً (Both)'),
    ]

    PRICING_TYPE_CHOICES = [
        ('per_second', 'حسب عدد الثواني (Per Second)'),
        ('flat', 'سعر ثابت لكل عملية (Flat Rate)'),
    ]

    # Model identity & Technical specifications (Locked & Immutable)
    name = models.CharField(
        max_length=150,
        verbose_name="اسم النموذج الظاهر للمستخدم",
        help_text="اسم النموذج الرسمي النظيف كما يظهر في واجهة الاستوديو بدون ذكر المزودات"
    )
    model_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="معرف النموذج البرمجي (Model ID)",
        help_text="المعرف التقني للنموذج في Crun AI"
    )
    provider = models.CharField(
        max_length=50,
        default='Crun AI',
        verbose_name="المزود",
        help_text="مزود الخدمة الأساسي (Crun AI)"
    )
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPE_CHOICES,
        default='per_second',
        verbose_name="آلية التسعير",
        help_text="طريقة احتساب التكلفة: بالثانية أو سعر ثابت"
    )
    supported_resolutions = models.CharField(
        max_length=100,
        default='480p,720p,1080p,4k',
        verbose_name="الجودات المدعومة",
        help_text="الجودات المدعومة مفصولة بفاصلة مثل: 480p,720p,1080p,4k"
    )
    min_duration = models.IntegerField(
        default=5,
        verbose_name="الحد الأدنى للمدة (ثواني)",
        help_text="أقل مدة فيديو مسموحة بالثواني"
    )
    max_duration = models.IntegerField(
        default=60,
        verbose_name="الحد الأقصى للمدة (ثواني)",
        help_text="أقصى مدة فيديو مسموحة بالثواني"
    )
    allowed_durations = models.JSONField(
        blank=True,
        null=True,
        verbose_name="المدد المحددة (إن وجدت)",
        help_text="قائمة بالمدد الثابتة إن كان النموذج لا يدعم سوى مدد معينة"
    )

    # Dynamic Pricing fields (Fully customizable by Admin)
    cost_480p = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="سعر جودة 480p (رصيد/ثانية)",
        help_text="التكلفة لكل ثانية لجودة 480p (أو التكلفة الثابتة)"
    )
    cost_720p = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('2.00'),
        verbose_name="سعر جودة 720p (رصيد/ثانية)",
        help_text="التكلفة لكل ثانية لجودة 720p (أو التكلفة الثابتة)"
    )
    cost_1080p = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('3.50'),
        verbose_name="سعر جودة 1080p (رصيد/ثانية)",
        help_text="التكلفة لكل ثانية لجودة 1080p (أو التكلفة الثابتة)"
    )
    cost_4k = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('6.00'),
        verbose_name="سعر جودة 4K (رصيد/ثانية)",
        help_text="التكلفة لكل ثانية لجودة 4K (أو التكلفة الثابتة)"
    )
    cost_per_second = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('2.00'),
        verbose_name="التكلفة الافتراضية للثانية",
        help_text="تستخدم كاحتياط عند عدم تحديد جودة معينة"
    )

    # Operational settings (Customizable by Admin)
    allowed_wallet = models.CharField(
        max_length=20,
        choices=WALLET_CHOICES,
        default='both',
        verbose_name="المحفظة المسموحة",
        help_text="نوع الرصيد المسموح بالخصم منه لهذا النموذج"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعل في الاستوديو",
        help_text="إتاحة النموذج للمستخدمين في واجهة الاستوديو"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="نموذج افتراضي",
        help_text="النموذج المختار تلقائياً عند فتح الأداة"
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="ترتيب الظهور",
        help_text="ترتيب النموذج في القوائم المنسدلة"
    )

    class Meta:
        verbose_name = 'إعدادات نموذج الأفاتار الرقمي (Crun AI)'
        verbose_name_plural = 'نماذج الأفاتار الرقمي (Avatar Video Models)'
        ordering = ['sort_order', '-is_default', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        """
        Locks technical specifications from modifications once created in database.
        """
        super().clean()
        if self.pk:
            orig = AvatarVideoModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                locked_fields = ['name', 'model_id', 'provider', 'pricing_type', 'supported_resolutions', 'min_duration', 'max_duration']
                for f in locked_fields:
                    orig_val = getattr(orig, f)
                    new_val = getattr(self, f)
                    if orig_val != new_val:
                        raise ValidationError({
                            f: f"حقل '{f}' محمي ومقفل تقنياً ولا يمكن تعديله لضمان استقرار الربط مع Crun AI. يمكنك فقط تعديل الأسعار وحالة التفعيل والمحفظة."
                        })

    def save(self, *args, **kwargs):
        """
        Enforce technical lockdown on save: if existing record, technical fields remain identical to DB.
        """
        if self.pk:
            orig = AvatarVideoModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                self.name = orig.name
                self.model_id = orig.model_id
                self.provider = orig.provider
                self.pricing_type = orig.pricing_type
                self.supported_resolutions = orig.supported_resolutions
                self.min_duration = orig.min_duration
                self.max_duration = orig.max_duration
                self.allowed_durations = orig.allowed_durations

        if self.is_default:
            AvatarVideoModelConfig.objects.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def get_cost_for_resolution(self, resolution: str) -> Decimal:
        res = (resolution or '720p').lower().strip()
        if '4k' in res:
            return self.cost_4k
        elif '1080' in res:
            return self.cost_1080p
        elif '480' in res:
            return self.cost_480p
        return self.cost_720p

    def calculate_total_cost(self, resolution: str, duration_seconds: int) -> Decimal:
        rate = self.get_cost_for_resolution(resolution)
        if self.pricing_type == 'flat':
            return rate
        sec = max(self.min_duration, min(duration_seconds, self.max_duration))
        return Decimal(str(rate)) * Decimal(str(sec))


class AvatarVideoSetting(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name="تفعيل الأداة")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    max_audio_duration_seconds = models.IntegerField(default=120, verbose_name="أقصى مدة للتسجيل الصوتي (ثواني)")

    class Meta:
        verbose_name = 'الإعدادات العامة لأداة الأفاتار'
        verbose_name_plural = 'الإعدادات العامة لأداة الأفاتار'

    def __str__(self):
        return f"Avatar Video Settings (Enabled: {self.is_enabled})"
