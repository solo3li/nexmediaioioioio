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
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>',
        'badge': 'Cinematic 4K',
        'description': 'تحويل الأوامر النصية والمشاهد الوصفية إلى مقاطع فيديو بدقة تصل إلى 4K.',
        'template': 'studio/tools/text_to_video.html',
        'model_class': TextToVideoModelConfig,
    },
    'image-to-video': {
        'name_ar': 'تحريك الصور إلى فيديو',
        'name_en': 'Image to Video',
        'slug': 'image-to-video',
        'db_tool_type': 'image_to_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/><path d="m14 10 4 4"/></svg>',
        'badge': 'Motion',
        'description': 'تحويل الصور الثابتة إلى مشاهد فيديو حية ومتحركة مع توجيه حركة الكاميرا.',
        'template': 'studio/tools/image_to_video.html',
        'model_class': ImageToVideoModelConfig,
    },
    'text-to-image': {
        'name_ar': 'توليد الصور',
        'name_en': 'Text to Image',
        'slug': 'text-to-image',
        'db_tool_type': 'text_to_image',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>',
        'badge': 'Image Gen',
        'description': 'إنتاج تصاميم بصرية ولوحات إعلانية وفنية بدقة عالية وتفاصيل واقعية.',
        'template': 'studio/tools/text_to_image.html',
        'model_class': TextToImageModelConfig,
    },
    'tts': {
        'name_ar': 'تحويل النص إلى صوت (TTS)',
        'name_en': 'Text to Speech',
        'slug': 'tts',
        'db_tool_type': 'tts',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>',
        'badge': 'Voices',
        'description': 'تحويل النصوص المكتوبة إلى تسجيلات صوتية طبيعية بأصوات عربية وعالمية.',
        'template': 'studio/tools/tts.html',
        'model_class': TtsModelConfig,
    },
    'stt': {
        'name_ar': 'تفريغ الصوت (STT)',
        'name_en': 'Speech to Text',
        'slug': 'stt',
        'db_tool_type': 'stt',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10v4"/><path d="M7 6v12"/><path d="M11 3v18"/><path d="M15 8v8"/><path d="M19 5v14"/><path d="M23 10v4"/></svg>',
        'badge': 'Whisper',
        'description': 'استخراج النصوص من التسجيلات الصوتية ومقاطع الفيديو مع دعم ملفات الترجمة.',
        'template': 'studio/tools/stt.html',
        'model_class': SttModelConfig,
    },
    'reference-to-video': {
        'name_ar': 'الفيديو متعدد المراجع',
        'name_en': 'Reference to Video',
        'slug': 'reference-to-video',
        'db_tool_type': 'reference_to_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        'badge': 'Multi-Ref',
        'description': 'توليد مشاهد فيديو مع الاحتفاظ بهوية الشخصيات وتفاصيل الأزياء من صور مرجعية.',
        'template': 'studio/tools/reference_to_video.html',
        'model_class': ReferenceToVideoModelConfig,
    },
    'lipsync': {
        'name_ar': 'مزامنة حركة الشفاه',
        'name_en': 'Lip Sync',
        'slug': 'lipsync',
        'db_tool_type': 'lipsync',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c3-4 7-6 10-6s7 2 10 6c-3 4-7 6-10 6s-7-2-10-6Z"/><path d="M8 12c1.5 2 2.5 3 4 3s2.5-1 4-3"/></svg>',
        'badge': 'Lip Sync',
        'description': 'مطابقة حركة شفاه الشخصيات بدقة مع مسارات الصوت المنطوق بأي لغة.',
        'template': 'studio/tools/lipsync.html',
        'model_class': LipSyncModelConfig,
    },
    'motion-control': {
        'name_ar': 'التحكم الحركي (Motion)',
        'name_en': 'Motion Control',
        'slug': 'motion-control',
        'db_tool_type': 'motion_control',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"/><path d="M12 7v7"/><path d="m6 11 6 3 6-3"/><path d="m9 22 3-8 3 8"/></svg>',
        'badge': 'Motion',
        'description': 'نقل حركات الشخصيات من فيديو مرجعي إلى أي صورة مستهدفة.',
        'template': 'studio/tools/motion_control.html',
        'model_class': MotionControlModelConfig,
    },
    'avatar-video': {
        'name_ar': 'فيديو الأفاتار المتكلم',
        'name_en': 'Avatar Studio',
        'slug': 'avatar-video',
        'db_tool_type': 'avatar_video',
        'icon': '<svg class="tool-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        'badge': 'Avatar',
        'description': 'إنشاء مقدمي برامج افتراضيين وشخصيات متحدثة بتعبيرات وجه واقعية وطبيعية.',
        'template': 'studio/tools/avatar_video.html',
        'model_class': AvatarVideoModelConfig,
    },
}


def studio_redirect(request):
    """Redirects /studio/ to the primary tool /studio/text-to-video/"""
    return redirect('studio_tool', tool_slug='text-to-video')


def studio_tool_view(request, tool_slug):
    """Renders the dedicated page for a specific AI tool within the Royal Studio workspace"""
    if tool_slug not in TOOLS_METADATA:
        raise Http404(f"Tool '{tool_slug}' not found.")

    tool_meta = TOOLS_METADATA[tool_slug]
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
