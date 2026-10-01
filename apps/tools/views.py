from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404

from apps.history.models import GenerationHistory
from apps.tools.tts.models import TtsModelConfig, TtsVoice
from apps.tools.stt.models import SttModelConfig
from apps.tools.text_to_video.models import TextToVideoModelConfig
from apps.tools.image_to_video.models import ImageToVideoModelConfig
from apps.tools.reference_to_video.models import ReferenceToVideoModelConfig
from apps.tools.lipsync.models import LipSyncModelConfig
from apps.tools.motion_control.models import MotionControlModelConfig
from apps.tools.text_to_image.models import TextToImageModelConfig
from apps.tools.avatar_video.models import AvatarVideoModelConfig

User = get_user_model()

TOOLS_METADATA = {
    'text-to-video': {
        'name_ar': 'توليد الفيديو من النص',
        'name_en': 'Text to Video',
        'slug': 'text-to-video',
        'db_tool_type': 'text_to_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="m15 8-6 4 6 4V8Z"/></svg>',
        'badge': 'Cinematic 4K',
        'badge_ar': 'سينمائي 4K',
        'badge_en': 'Cinematic 4K',
        'description': 'تحويل الأوامر النصية والمشاهد الوصفية إلى مقاطع فيديو بدقة تصل إلى 4K.',
        'description_ar': 'تحويل الأوامر النصية والمشاهد الوصفية إلى مقاطع فيديو بدقة تصل إلى 4K.',
        'description_en': 'Transform text prompts and descriptive scenes into ultra-high-definition cinematic videos up to 4K.',
        'template': 'studio/tools/text_to_video.html',
        'model_class': TextToVideoModelConfig,
    },
    'image-to-video': {
        'name_ar': 'تحريك الصور إلى فيديو',
        'name_en': 'Image to Video',
        'slug': 'image-to-video',
        'db_tool_type': 'image_to_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/><path d="m14 8 2 2-2 2"/></svg>',
        'badge': 'Motion',
        'badge_ar': 'تحريك ذكي',
        'badge_en': 'Motion',
        'description': 'تحويل الصور الثابتة إلى مشاهد فيديو حية ومتحركة مع توجيه حركة الكاميرا.',
        'description_ar': 'تحويل الصور الثابتة إلى مشاهد فيديو حية ومتحركة مع توجيه حركة الكاميرا.',
        'description_en': 'Animate still photographs and digital artwork into fluid, dynamic video sequences with camera control.',
        'template': 'studio/tools/image_to_video.html',
        'model_class': ImageToVideoModelConfig,
    },
    'text-to-image': {
        'name_ar': 'توليد الصور',
        'name_en': 'Text to Image',
        'slug': 'text-to-image',
        'db_tool_type': 'text_to_image',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>',
        'badge': 'Image Gen',
        'badge_ar': 'توليد صور',
        'badge_en': 'Image Gen',
        'description': 'إنتاج تصاميم بصرية ولوحات إعلانية وفنية بدقة عالية وتفاصيل واقعية.',
        'description_ar': 'إنتاج تصاميم بصرية ولوحات إعلانية وفنية بدقة عالية وتفاصيل واقعية.',
        'description_en': 'Create photorealistic visuals, digital illustrations, and commercial artwork with high-resolution details.',
        'template': 'studio/tools/text_to_image.html',
        'model_class': TextToImageModelConfig,
    },
    'tts': {
        'name_ar': 'تحويل النص إلى صوت (TTS)',
        'name_en': 'Text to Speech',
        'slug': 'tts',
        'db_tool_type': 'tts',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>',
        'badge': 'Voices',
        'badge_ar': 'أصوات طبيعية',
        'badge_en': 'Voices',
        'description': 'تحويل النصوص المكتوبة إلى تسجيلات صوتية طبيعية بأصوات عربية وعالمية.',
        'description_ar': 'تحويل النصوص المكتوبة إلى تسجيلات صوتية طبيعية بأصوات عربية وعالمية.',
        'description_en': 'Synthesize written scripts into ultra-realistic human voices with multilingual accents and emotional depth.',
        'template': 'studio/tools/tts.html',
        'model_class': TtsModelConfig,
    },
    'stt': {
        'name_ar': 'تفريغ الصوت (STT)',
        'name_en': 'Speech to Text',
        'slug': 'stt',
        'db_tool_type': 'stt',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>',
        'badge': 'Whisper',
        'badge_ar': 'تفريغ ذكي',
        'badge_en': 'Whisper',
        'description': 'استخراج النصوص من التسجيلات الصوتية ومقاطع الفيديو مع دعم ملفات الترجمة.',
        'description_ar': 'استخراج النصوص من التسجيلات الصوتية ومقاطع الفيديو مع دعم ملفات الترجمة.',
        'description_en': 'Transcribe spoken audio and video files into precise timestamps and text transcripts in seconds.',
        'template': 'studio/tools/stt.html',
        'model_class': SttModelConfig,
    },
    'reference-to-video': {
        'name_ar': 'الفيديو متعدد المراجع',
        'name_en': 'Reference to Video',
        'slug': 'reference-to-video',
        'db_tool_type': 'reference_to_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-8.58 3.91a2 2 0 0 1-1.66 0L2 12.5"/><path d="m22 17.5-8.58 3.91a2 2 0 0 1-1.66 0L2 17.5"/></svg>',
        'badge': 'Multi-Ref',
        'badge_ar': 'مراجع متعددة',
        'badge_en': 'Multi-Ref',
        'description': 'توليد مشاهد فيديو مع الاحتفاظ بهوية الشخصيات وتفاصيل الأزياء من صور مرجعية.',
        'description_ar': 'توليد مشاهد فيديو مع الاحتفاظ بهوية الشخصيات وتفاصيل الأزياء من صور مرجعية.',
        'description_en': 'Produce cinema-grade videos while preserving character identity and clothing across multiple image references.',
        'template': 'studio/tools/reference_to_video.html',
        'model_class': ReferenceToVideoModelConfig,
    },
    'lipsync': {
        'name_ar': 'مزامنة حركة الشفاه',
        'name_en': 'Lip Sync',
        'slug': 'lipsync',
        'db_tool_type': 'lipsync',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v14"/><path d="M22 10v3"/></svg>',
        'badge': 'Lip Sync',
        'badge_ar': 'مزامنة دقيقة',
        'badge_en': 'Lip Sync',
        'description': 'مطابقة حركة شفاه الشخصيات بدقة مع مسارات الصوت المنطوق بأي لغة.',
        'description_ar': 'مطابقة حركة شفاه الشخصيات بدقة مع مسارات الصوت المنطوق بأي لغة.',
        'description_en': 'Synchronize character mouth movements flawlessly with spoken speech tracks in any language.',
        'template': 'studio/tools/lipsync.html',
        'model_class': LipSyncModelConfig,
    },
    'motion-control': {
        'name_ar': 'التحكم الحركي (Motion)',
        'name_en': 'Motion Control',
        'slug': 'motion-control',
        'db_tool_type': 'motion_control',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v16h16"/><path d="m5 19 6-6"/><path d="m2 6 3-3 3 3"/><path d="m18 16 3 3-3 3"/></svg>',
        'badge': 'Motion',
        'badge_ar': 'توجيه حركي',
        'badge_en': 'Motion',
        'description': 'نقل حركات الشخصيات من فيديو مرجعي إلى أي صورة مستهدفة.',
        'description_ar': 'نقل حركات الشخصيات من فيديو مرجعي إلى أي صورة مستهدفة.',
        'description_en': 'Transfer complex body movements, dances, and gestures from a driving video onto any target image.',
        'template': 'studio/tools/motion_control.html',
        'model_class': MotionControlModelConfig,
    },
    'avatar-video': {
        'name_ar': 'فيديو الأفاتار المتكلم',
        'name_en': 'Avatar Studio',
        'slug': 'avatar-video',
        'db_tool_type': 'avatar_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="14" x="3" y="3" rx="2"/><circle cx="12" cy="9" r="2.5"/><path d="M8 15a4 4 0 0 1 8 0"/><path d="m9 21 3-4 3 4"/></svg>',
        'badge': 'Avatar',
        'badge_ar': 'أفاتار واقعي',
        'badge_en': 'Avatar',
        'description': 'إنشاء مقدمي برامج افتراضيين وشخصيات متحدثة بتعبيرات وجه واقعية وطبيعية.',
        'description_ar': 'إنشاء مقدمي برامج افتراضيين وشخصيات متحدثة بتعبيرات وجه واقعية وطبيعية.',
        'description_en': 'Create realistic digital presenters and speaking avatars with expressive facial gestures from text or audio.',
        'template': 'studio/tools/avatar_video.html',
        'model_class': AvatarVideoModelConfig,
    },
}


def studio_redirect(request):
    """Redirects /studio/ to the primary tool /studio/text-to-video/"""
    return redirect('studio_tool', tool_slug='text-to-video')


def studio_tool_view(request, tool_slug):
    """Renders the dedicated page for a specific AI tool within the Royal Studio workspace"""
    slug_key = tool_slug.replace('_', '-')
    if slug_key not in TOOLS_METADATA and tool_slug in TOOLS_METADATA:
        slug_key = tool_slug
    if slug_key not in TOOLS_METADATA:
        raise Http404(f"Tool '{tool_slug}' not found.")

    tool_meta = TOOLS_METADATA[slug_key]
    user = request.user
    if not user.is_authenticated:
        user = User.objects.filter(is_superuser=True).first()

    # Fetch models for this tool
    model_class = tool_meta.get('model_class')
    if model_class:
        try:
            models_list = model_class.objects.filter(is_active=True).order_by('sort_order', '-is_default', 'name')
        except Exception:
            models_list = model_class.objects.filter(is_active=True)
    else:
        models_list = []

    # Extra tool data
    extra_context = {}
    if tool_slug == 'tts':
        extra_context['tts_voices'] = TtsVoice.objects.filter(is_active=True)

    # Tool specific recent history
    db_tool_type = tool_meta['db_tool_type']
    recent_history = GenerationHistory.objects.filter(
        user=user,
        tool_type__icontains=db_tool_type
    ).order_by('-created_at')[:8] if user else []

    context = {
        'current_tool': tool_meta,
        'all_tools': list(TOOLS_METADATA.values()),
        'active_user': user,
        'models': models_list,
        'recent_history': recent_history,
        **extra_context,
    }
    return render(request, tool_meta['template'], context)
