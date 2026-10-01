from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models


class SttModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'الرصيد الأساسي (Standard)'),
        ('premium', 'الرصيد المميز (Premium)'),
        ('both', 'المحفظتان معاً (Both)'),
    ]

    PRICING_TYPE_CHOICES = [
        ('per_minute', 'حسب الدقيقة المحسوبة بالثواني (Per Minute)'),
        ('flat', 'سعر ثابت مقطوع لكل ملف (Flat Rate)'),
    ]

    # Model identity & specifications (Locked & Immutable)
    name = models.CharField(
        max_length=150,
        verbose_name="اسم النموذج الظاهر للمستخدم",
        help_text="اسم النموذج الرسمي كما يظهر في واجهة الاستوديو بدون ذكر المزودات"
    )
    model_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="معرف النموذج البرمجي (Model ID)",
        help_text="المعرف التقني للنموذج في OpenAI (مثل whisper-1)"
    )
    provider = models.CharField(
        max_length=50,
        default='OpenAI',
        verbose_name="المزود",
        help_text="مزود الخدمة الأساسي (OpenAI)"
    )
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPE_CHOICES,
        default='per_minute',
        verbose_name="آلية التسعير",
        help_text="طريقة احتساب التكلفة: بالدقيقة أو سعر ثابت"
    )
    min_duration_seconds = models.IntegerField(
        default=1,
        verbose_name="الحد الأدنى للمدة (ثواني)",
        help_text="أقل مدة صوتية مسموحة بالثواني"
    )
    max_duration_seconds = models.IntegerField(
        default=3600,
        verbose_name="الحد الأقصى للمدة (ثواني)",
        help_text="أقصى مدة صوتية مسموحة بالثواني (افتراضياً 3600 ثانية = 60 دقيقة)"
    )

    # Dynamic Pricing Fields (Editable by Admin)
    cost_per_minute = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name="سعر الدقيقة (رصيد/دقيقة)",
        help_text="تكلفة التفريغ الصوتي لكل دقيقة كاملة"
    )
    cost_per_second = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0167'),
        verbose_name="سعر الثانية (رصيد/ثانية)",
        help_text="تكلفة الثانية (تُحسب تلقائياً أو تُحدد كحد أدنى للثواني)"
    )

    # Operational settings
    allowed_wallet = models.CharField(
        max_length=20,
        choices=WALLET_CHOICES,
        default='standard',
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
        verbose_name = 'إعدادات نموذج تفريغ الصوت (OpenAI Whisper)'
        verbose_name_plural = 'نماذج تفريغ الصوت (STT Models)'
        ordering = ['sort_order', '-is_default', 'name']

    def __str__(self):
        return f"{self.name} - {self.cost_per_minute} رصيد/دقيقة"

    def clean(self):
        super().clean()
        if self.pk:
            orig = SttModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                locked_fields = ['name', 'model_id', 'provider', 'pricing_type', 'min_duration_seconds', 'max_duration_seconds']
                for f in locked_fields:
                    orig_val = getattr(orig, f)
                    new_val = getattr(self, f)
                    if orig_val != new_val:
                        raise ValidationError({
                            f: f"حقل '{f}' محمي ومقفل تقنياً ولا يمكن تعديله لضمان استقرار الربط مع OpenAI Whisper. يمكنك فقط تعديل الأسعار وحالة التفعيل والمحفظة."
                        })

    def save(self, *args, **kwargs):
        if self.pk:
            orig = SttModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                self.name = orig.name
                self.model_id = orig.model_id
                self.provider = orig.provider
                self.pricing_type = orig.pricing_type
                self.min_duration_seconds = orig.min_duration_seconds
                self.max_duration_seconds = orig.max_duration_seconds

        if self.is_default:
            SttModelConfig.objects.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def calculate_total_cost(self, duration_seconds: int) -> Decimal:
        if self.pricing_type == 'flat':
            return self.cost_per_minute

        sec = max(self.min_duration_seconds, min(duration_seconds, self.max_duration_seconds))
        # Rate per second calculated precisely from cost_per_minute / 60
        rate_per_sec = self.cost_per_minute / Decimal('60.0')
        total = Decimal(str(sec)) * rate_per_sec
        # Round to 2 decimal places with minimum 0.05
        return max(Decimal('0.05'), round(total, 2))


class SttSetting(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name="تفعيل الأداة")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    max_file_size_mb = models.IntegerField(default=50, verbose_name="أقصى حجم ملف صوتي (ميغابايت)")
    max_duration_minutes = models.IntegerField(default=30, verbose_name="أقصى مدة تسجيل (دقائق)")

    class Meta:
        verbose_name = 'الإعدادات العامة لأداة تفريغ الصوت'
        verbose_name_plural = 'الإعدادات العامة لأداة تفريغ الصوت'

    def __str__(self):
        return f"STT Settings (Enabled: {self.is_enabled})"
