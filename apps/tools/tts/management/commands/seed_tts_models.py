from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.tools.tts.models import TtsModelConfig, TtsVoice


class Command(BaseCommand):
    help = 'Seeds all 3 official Google Gemini TTS models and 30 customized human voice persona profiles'

    def handle(self, *args, **options):
        # 1. Seed Models
        models_data = [
            {
                'name': 'Neural Studio 2.5 Pro HD (High Quality)',
                'model_id': 'gemini-2.5-pro-tts',
                'provider': 'Google Gemini',
                'quality_tier': 'high',
                'chars_per_block': 500,
                'cost_per_block_standard': Decimal('0.5000'),
                'cost_per_block_high': Decimal('1.0000'),
                'cost_per_char': Decimal('0.00200'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
                'sort_order': 1,
            },
            {
                'name': 'Neural Audio 3.1 Flash Ultra',
                'model_id': 'gemini-3.1-flash-tts',
                'provider': 'Google Gemini',
                'quality_tier': 'standard',
                'chars_per_block': 500,
                'cost_per_block_standard': Decimal('0.4000'),
                'cost_per_block_high': Decimal('0.8000'),
                'cost_per_char': Decimal('0.00150'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': False,
                'sort_order': 2,
            },
            {
                'name': 'Neural Express 2.5 Flash (Standard Quality)',
                'model_id': 'gemini-2.5-flash-tts',
                'provider': 'Google Gemini',
                'quality_tier': 'standard',
                'chars_per_block': 500,
                'cost_per_block_standard': Decimal('0.3000'),
                'cost_per_block_high': Decimal('0.6000'),
                'cost_per_char': Decimal('0.00100'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': False,
                'sort_order': 3,
            },
        ]

        m_count = 0
        for m_data in models_data:
            existing = TtsModelConfig.objects.filter(model_id=m_data['model_id']).first()
            if existing:
                TtsModelConfig.objects.filter(id=existing.id).update(**m_data)
            else:
                TtsModelConfig.objects.create(**m_data)
            m_count += 1

        # 2. Seed 30 Customized Voice Profiles (Disguised Google Profiles)
        voices_data = [
            {'voice_id': 'Puck', 'display_name_ar': 'عمر المنصور (شبابي وحيوي)', 'display_name': 'Omar (Dynamic & Youthful)', 'gender': 'Male', 'voice_category': 'dynamic', 'accent_note': 'صوت شبابي مفعم بالحيوية ممتاز للإعلانات ومحتوى السوشيال ميديا', 'sort_order': 1},
            {'voice_id': 'Charon', 'display_name_ar': 'خالد الراشد (وثائقي ووقور)', 'display_name': 'Khaled (Deep & Authoritative)', 'gender': 'Male', 'voice_category': 'formal', 'accent_note': 'نبرة عميقة رخيمة ذات وقار رسمي ومناسب للأفلام الوثائقية', 'sort_order': 2},
            {'voice_id': 'Kore', 'display_name_ar': 'سارة العلي (هادئ ودافئ)', 'display_name': 'Sarah (Calm & Melodic)', 'gender': 'Female', 'voice_category': 'warm', 'accent_note': 'نبرة أنثوية دافئة ومتزنة تلائم الروايات والمحتوى الإنساني', 'sort_order': 3},
            {'voice_id': 'Fenrir', 'display_name_ar': 'طارق المهدي (سينمائي درامي)', 'display_name': 'Tariq (Cinematic & Resonant)', 'gender': 'Male', 'voice_category': 'dramatic', 'accent_note': 'صوت درامي ذو صدى عريض ومؤثر مناسب للإعلانات الكبرى والمقدمات', 'sort_order': 4},
            {'voice_id': 'Aoede', 'display_name_ar': 'ليلى النجار (إذاعي جذاب)', 'display_name': 'Laila (Broadcast & Eloquent)', 'gender': 'Female', 'voice_category': 'storytelling', 'accent_note': 'أداء إذاعي فصيح ونطق مخارج حروف بالغ الدقة والجمال', 'sort_order': 5},
            {'voice_id': 'Leda', 'display_name_ar': 'مريم الشريف (تنفيذي للأعمال)', 'display_name': 'Mariam (Corporate Executive)', 'gender': 'Female', 'voice_category': 'formal', 'accent_note': 'نبرة احترافية واثقة مثالية للعروض التقديمية والتقارير المالية', 'sort_order': 6},
            {'voice_id': 'Orus', 'display_name_ar': 'فارس السعدي (حماسي تسويقي)', 'display_name': 'Faris (Commercial & Inspiring)', 'gender': 'Male', 'voice_category': 'dynamic', 'accent_note': 'إلقاء تسويقي ملهم يحفز على الشراء والتفاعل الفوري', 'sort_order': 7},
            {'voice_id': 'Zephyr', 'display_name_ar': 'ياسمين فريد (سرد قصصي وروايات)', 'display_name': 'Yasmine (Gentle Storyteller)', 'gender': 'Female', 'voice_category': 'storytelling', 'accent_note': 'صوت سردي عذب يأخذ المستمع في رحلة خيالية عبر الفصول', 'sort_order': 8},
            {'voice_id': 'Callisto', 'display_name_ar': 'هدى سلطان (إخباري رصين)', 'display_name': 'Huda (Confident News Anchor)', 'gender': 'Female', 'voice_category': 'formal', 'accent_note': 'مذيعة أخبار متمرسة مع تحكم تام بالنبرة المحايدة والواثقة', 'sort_order': 9},
            {'voice_id': 'Io', 'display_name_ar': 'سفيان الأحمد (بودكاست وحوارات)', 'display_name': 'Sufian (Conversational Podcaster)', 'gender': 'Male', 'voice_category': 'warm', 'accent_note': 'نبرة حوارية عفوية قريبة من القلب مثالية للبرامج الصوتية', 'sort_order': 10},
            {'voice_id': 'Europa', 'display_name_ar': 'نور الهدى (تعليمي وأكاديمي)', 'display_name': 'Noor (Academic & Explainer)', 'gender': 'Female', 'voice_category': 'educational', 'accent_note': 'صوت تعليمي واضح ومبسط للمنصات الأكاديمية والشروحات', 'sort_order': 11},
            {'voice_id': 'Ganymede', 'display_name_ar': 'زيد الحكيم (فلسفي وعميق)', 'display_name': 'Zaid (Rich & Philosophical)', 'gender': 'Male', 'voice_category': 'dramatic', 'accent_note': 'نبرة صوتية حكيمة تلائم النصوص الفكرية والاقتباسات العميقة', 'sort_order': 12},
            {'voice_id': 'Titan', 'display_name_ar': 'حمزة الشامي (خطابي وقوي)', 'display_name': 'Hamza (Powerful Keynote Speaker)', 'gender': 'Male', 'voice_category': 'formal', 'accent_note': 'صوت خطابي جهوري وقوي يشد انتباه الجماهير في الفعاليات', 'sort_order': 13},
            {'voice_id': 'Enceladus', 'display_name_ar': 'ريما العبدالله (لطيف وناعم)', 'display_name': 'Rima (Soft & Empathetic)', 'gender': 'Female', 'voice_category': 'warm', 'accent_note': 'صوت ناعم ومريح للأذن يعزز الثقة في الإرشادات الصوتية', 'sort_order': 14},
            {'voice_id': 'Mimas', 'display_name_ar': 'كريم عثمان (مساعد ذكي وواضح)', 'display_name': 'Karim (Clear Virtual Assistant)', 'gender': 'Male', 'voice_category': 'educational', 'accent_note': 'وضوح صوتي بلوري وتناغم نغمي رائع للمساعدين الرقميين', 'sort_order': 15},
            {'voice_id': 'Rhea', 'display_name_ar': 'منى الخالد (إعلامي معاصر)', 'display_name': 'Mona (Contemporary Host)', 'gender': 'Female', 'voice_category': 'dynamic', 'accent_note': 'نبرة إعلامية حيوية وعصرية تناسب برامج الشباب والمجلات الرقمية', 'sort_order': 16},
            {'voice_id': 'Dione', 'display_name_ar': 'جمانة حسني (إعلانات فاخرة)', 'display_name': 'Jumana (Luxury Commercials)', 'gender': 'Female', 'voice_category': 'luxury', 'accent_note': 'صوت أرستقراطي راقٍ مخصص للمنتجات الفارهة والعلامات العالمية', 'sort_order': 17},
            {'voice_id': 'Tethys', 'display_name_ar': 'سلمى جاد (تأمل واسترخاء)', 'display_name': 'Salma (Meditation & Mindfulness)', 'gender': 'Female', 'voice_category': 'warm', 'accent_note': 'نبرة استرخائية بطيئة الإيقاع تساعد على التأمل وتصفية الذهن', 'sort_order': 18},
            {'voice_id': 'Iapetus', 'display_name_ar': 'ياسين مراد (تاريخي وسردي)', 'display_name': 'Yassin (Historic Chronicler)', 'gender': 'Male', 'voice_category': 'storytelling', 'accent_note': 'أداء راوٍ تاريخي يستحضر الأحداث والملاحم بأسلوب شائق', 'sort_order': 19},
            {'voice_id': 'Hyperion', 'display_name_ar': 'أدهم القاضي (رسمي وقانوني)', 'display_name': 'Adham (Formal Legal & Official)', 'gender': 'Male', 'voice_category': 'formal', 'accent_note': 'دقة صارمة ونبرة قانونية تناسب البيانات الرسمية والسياسات', 'sort_order': 20},
            {'voice_id': 'Oberon', 'display_name_ar': 'بسام كمال (مسرحي وكتب صوتية)', 'display_name': 'Bassam (Theatrical Audiobooks)', 'gender': 'Male', 'voice_category': 'dramatic', 'accent_note': 'قدرة متميزة على تقمص الشخصيات وتلوين الصوت في الكتب الصوتية', 'sort_order': 21},
            {'voice_id': 'Titania', 'display_name_ar': 'رزان شاهين (درامي مسرحي)', 'display_name': 'Razan (Dramatic Thespian)', 'gender': 'Female', 'voice_category': 'dramatic', 'accent_note': 'شحنات عاطفية متوازنة وتعبير درامي راقٍ للروايات والمسرح', 'sort_order': 22},
            {'voice_id': 'Ariel', 'display_name_ar': 'دينا عادل (مشرق وتفاؤلي)', 'display_name': 'Dina (Bright & Inspiring)', 'gender': 'Female', 'voice_category': 'dynamic', 'accent_note': 'طاقة إيجابية ونبرة مبهجة تبعث على التفاؤل والنشاط', 'sort_order': 23},
            {'voice_id': 'Umbriel', 'display_name_ar': 'غسان توفيق (غموض وتشويق)', 'display_name': 'Ghassan (Mystery & Suspense)', 'gender': 'Male', 'voice_category': 'dramatic', 'accent_note': 'نبرة هامسة مشوقة مثالية لقصص الغموض وأفلام الإثارة', 'sort_order': 24},
            {'voice_id': 'Miranda', 'display_name_ar': 'شهد فوزي (حكايا وقصص أطفال)', 'display_name': 'Shahd (Children Storyteller)', 'gender': 'Female', 'voice_category': 'storytelling', 'accent_note': 'أسلوب قصصي مرح ومحبب للأطفال مع مخارج حروف سهلة وممتعة', 'sort_order': 25},
            {'voice_id': 'Triton', 'display_name_ar': 'سامي بركات (رياضي وحماسي)', 'display_name': 'Sami (High-Energy Sports)', 'gender': 'Male', 'voice_category': 'dynamic', 'accent_note': 'صوت رياضي حماسي وسريع التفاعل للأحداث الرياضية المشتعلة', 'sort_order': 26},
            {'voice_id': 'Proteus', 'display_name_ar': 'مالك عبدالكريم (متعدد الأداء)', 'display_name': 'Malek (Adaptive Voice Actor)', 'gender': 'Male', 'voice_category': 'educational', 'accent_note': 'صوت مرن يتكيف تلقائياً مع طابع النص العربي المكتوب', 'sort_order': 27},
            {'voice_id': 'Nereid', 'display_name_ar': 'حنين الباشا (رومانسي وشاعري)', 'display_name': 'Haneen (Poetic & Nostalgic)', 'gender': 'Female', 'voice_category': 'warm', 'accent_note': 'نبرة شاعرية رومانسية مفعمة بالحنين والإحساس المرهف', 'sort_order': 28},
            {'voice_id': 'Larissa', 'display_name_ar': 'أروى الميمان (برامج حوارية)', 'display_name': 'Arwa (Talk Show Host)', 'gender': 'Female', 'voice_category': 'dynamic', 'accent_note': 'صوت تفاعلي أنيق ملائم لمقابلات الحوار المباشرة والبرامج', 'sort_order': 29},
            {'voice_id': 'Galatea', 'display_name_ar': 'سيرين جمال (فخامة وبرستيج)', 'display_name': 'Cyrine (Luxury Prestige)', 'gender': 'Female', 'voice_category': 'luxury', 'accent_note': 'صوت يجسد الفخامة والأناقة في أبهى صورها للإعلانات الملكية', 'sort_order': 30},
        ]

        v_count = 0
        for v_data in voices_data:
            existing_v = TtsVoice.objects.filter(voice_id=v_data['voice_id']).first()
            if existing_v:
                TtsVoice.objects.filter(id=existing_v.id).update(**v_data)
            else:
                TtsVoice.objects.create(**v_data)
            v_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {m_count} Gemini TTS models and {v_count} human voice profiles!"))
