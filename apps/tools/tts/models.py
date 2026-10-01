import math
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models


class TtsModelConfig(models.Model):
    WALLET_CHOICES = [
        ('standard', 'الرصيد الأساسي (Standard)'),
        ('premium', 'الرصيد المميز (Premium)'),
        ('both', 'المحفظتان معاً (Both)'),
    ]

    QUALITY_TIER_CHOICES = [
        ('standard', 'جودة قياسية (Standard Quality)'),
        ('high', 'جودة فائقة سينمائية (High Quality Studio)'),
    ]

    # Model specifications (Locked & Immutable)
    name = models.CharField(
        max_length=150,
        verbose_name="اسم النموذج الظاهر للمستخدم",
        help_text="اسم النموذج الرسمي النظيف كما يظهر في واجهة الاستوديو بدون ذكر المزودات"
    )
    model_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="معرف النموذج البرمجي (Model ID)",
        help_text="المعرف التقني للنموذج في Google Gemini (مثل gemini-2.5-pro-tts)"
    )
    provider = models.CharField(
        max_length=50,
        default='Google Gemini',
        verbose_name="المزود",
        help_text="مزود الخدمة الأساسي (Google Gemini)"
    )
    quality_tier = models.CharField(
        max_length=20,
        choices=QUALITY_TIER_CHOICES,
        default='standard',
        verbose_name="مستوى الجودة للنموذج",
        help_text="المستوى الجودوي الأساسي للنموذج: قياسي أو فائق"
    )

    # Block-based Dynamic Pricing (Editable by Admin)
    chars_per_block = models.IntegerField(
        default=500,
        verbose_name="عدد الحروف في كل بلوك (Chars Per Block)",
        help_text="عدد الحروف المكونة للبلوك الواحد للتسعير (افتراضياً 500 حرف)"
    )
    cost_per_block_standard = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.5000'),
        verbose_name="سعر البلوك للجودة العادية (رصيد/بلوك)",
        help_text="تكلفة البلوك الواحد عند اختيار الجودة العادية (Normal Quality)"
    )
    cost_per_block_high = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name="سعر البلوك للجودة العالية (رصيد/بلوك)",
        help_text="تكلفة البلوك الواحد عند اختيار الجودة الفائقة (High Quality Studio)"
    )
    cost_per_char = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        default=Decimal('0.00100'),
        verbose_name="تكلفة الحرف الواحد (احتياط)",
        help_text="تستخدم كاحتياط عند عدم الاعتماد على البلوكات"
    )

    # Operational settings
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
        verbose_name = 'إعدادات نموذج الصوت (Google Gemini TTS)'
        verbose_name_plural = 'نماذج الصوت (TTS Models)'
        ordering = ['sort_order', '-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_quality_tier_display()})"

    def clean(self):
        super().clean()
        if self.pk:
            orig = TtsModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                locked_fields = ['name', 'model_id', 'provider', 'quality_tier']
                for f in locked_fields:
                    orig_val = getattr(orig, f)
                    new_val = getattr(self, f)
                    if orig_val != new_val:
                        raise ValidationError({
                            f: f"حقل '{f}' محمي ومقفل تقنياً ولا يمكن تعديله لضمان استقرار الربط مع Google Gemini. يمكنك فقط تعديل أسعار البلوكات وحجم البلوك وحالة التفعيل والمحفظة."
                        })

    def save(self, *args, **kwargs):
        if self.pk:
            orig = TtsModelConfig.objects.filter(pk=self.pk).first()
            if orig:
                self.name = orig.name
                self.model_id = orig.model_id
                self.provider = orig.provider
                self.quality_tier = orig.quality_tier

        if self.is_default:
            TtsModelConfig.objects.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def calculate_total_cost(self, char_count: int, quality_mode: str = None) -> Decimal:
        cnt = max(1, int(char_count or 1))
        blk_size = max(1, self.chars_per_block)
        blocks = math.ceil(cnt / blk_size)

        mode = (quality_mode or self.quality_tier or 'standard').lower().strip()
        if 'high' in mode or 'pro' in mode:
            rate = self.cost_per_block_high
        else:
            rate = self.cost_per_block_standard

        total = Decimal(str(blocks)) * Decimal(str(rate))
        return max(Decimal('0.10'), round(total, 2))


class TtsVoice(models.Model):
    GENDER_CHOICES = [
        ('Male', 'ذكر (Male)'),
        ('Female', 'أنثى (Female)'),
    ]

    CATEGORY_CHOICES = [
        ('formal', 'رسمي وإخباري (Formal & News)'),
        ('warm', 'ودود ودافئ (Warm & Conversational)'),
        ('dynamic', 'حماسي وإعلاني (Commercial & Energetic)'),
        ('dramatic', 'درامي وسينمائي (Dramatic & Cinematic)'),
        ('storytelling', 'سرد قصصي (Storytelling & Audiobooks)'),
        ('educational', 'تعليمي وأكاديمي (Educational & Explainer)'),
        ('luxury', 'فخامة وبرستيج (Luxury & Prestige)'),
    ]

    voice_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="معرف الصوت التقني (Voice ID)",
        help_text="معرف الصوت في Google Gemini Live/TTS (مثل Kore, Puck, Charon, Fenrir...)"
    )
    display_name = models.CharField(
        max_length=100,
        verbose_name="الاسم بالإنجليزية (Persona Name EN)",
        help_text="اسم الشخصية الإذاعية بالإنجليزية"
    )
    display_name_ar = models.CharField(
        max_length=100,
        verbose_name="الاسم بالعربية (Persona Name AR)",
        help_text="اسم الشخصية الإذاعية بالعربية بدون ذكر المصدر"
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='Male',
        verbose_name="الجنس"
    )
    voice_category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='formal',
        verbose_name="تصنيف الصوت وأسلوبه"
    )
    provider = models.CharField(
        max_length=50,
        default='Google Gemini',
        verbose_name="المزود"
    )
    accent_note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="وصف النبرة التعبيرية",
        help_text="وصف النبرة وطبيعة الأداء"
    )
    language_code = models.CharField(
        max_length=20,
        default='multilingual',
        verbose_name="رمز اللغة"
    )
    preview_audio_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="رابط عينة الصوت")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    sort_order = models.IntegerField(default=0, verbose_name="ترتيب الظهور")

    class Meta:
        verbose_name = 'شخصية ونبرة صوتية (TTS Voice Profile)'
        verbose_name_plural = 'بروفايلات الأصوات (TTS Voices)'
        ordering = ['sort_order', 'display_name_ar']

    def __str__(self):
        return f"{self.display_name_ar} ({self.get_gender_display()}) - {self.get_voice_category_display()}"


class TtsSetting(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name="تفعيل الأداة")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    max_chars = models.IntegerField(default=10000, verbose_name="الحد الأقصى لعدد الحروف في الطلب")

    class Meta:
        verbose_name = 'الإعدادات العامة لأداة تحويل النص إلى صوت'
        verbose_name_plural = 'الإعدادات العامة لأداة تحويل النص إلى صوت'

    def __str__(self):
        return f"TTS Settings (Enabled: {self.is_enabled})"
