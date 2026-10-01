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
        'icon': '🎬',
        'badge': 'Cinematic 4K',
        'description': 'تحويل الأوامر النصية والمشاهد الوصفية إلى مقاطع فيديو سينمائية فائقة الجودة بدقة تصل إلى 4K.',
        'template': 'studio/tools/text_to_video.html',
        'model_class': TextToVideoModelConfig,
    },
    'image-to-video': {
        'name_ar': 'تحريك الصور إلى فيديو',
        'name_en': 'Image to Video',
        'slug': 'image-to-video',
        'db_tool_type': 'image_to_video',
        'icon': '🎞️',
        'badge': 'Neural Motion',
        'description': 'تحويل الصور الثابتة إلى مشاهد فيديو حية ومتحركة مع توجيه ذكي لمسار الكاميرا وزوايا الرؤية.',
        'template': 'studio/tools/image_to_video.html',
        'model_class': ImageToVideoModelConfig,
    },
    'text-to-image': {
        'name_ar': 'توليد الصور التشكيلية',
        'name_en': 'Text to Image',
        'slug': 'text-to-image',
        'db_tool_type': 'text_to_image',
        'icon': '🎨',
        'badge': 'Grok & Imagen 3',
        'description': 'إنتاج تصاميم بصرية ولوحات إعلانية وفنية فائقة الجمال بدقة عالية وواقعية مذهلة.',
        'template': 'studio/tools/text_to_image.html',
        'model_class': TextToImageModelConfig,
    },
    'tts': {
        'name_ar': 'تحويل النص إلى صوت (TTS)',
        'name_en': 'Text to Speech',
        'slug': 'tts',
        'db_tool_type': 'tts',
        'icon': '🎙️',
        'badge': 'Neural Voices',
        'description': 'تحويل النصوص المكتوبة إلى نبرات صوتية بشرية حية بأصوات عربية وعالمية متميزة.',
        'template': 'studio/tools/tts.html',
        'model_class': TtsModelConfig,
    },
    'stt': {
        'name_ar': 'تفريغ الصوت الذكي (STT)',
        'name_en': 'Speech to Text',
        'slug': 'stt',
        'db_tool_type': 'stt',
        'icon': '🎧',
        'badge': 'Whisper Large v3',
        'description': 'استخراج النصوص من التسجيلات الصوتية ومقاطع الفيديو بدقة متناهية مع دعم التصدير لملفات الترجمة.',
        'template': 'studio/tools/stt.html',
        'model_class': SttModelConfig,
    },
    'reference-to-video': {
        'name_ar': 'الفيديو متعدد المراجع',
        'name_en': 'Reference to Video',
        'slug': 'reference-to-video',
        'db_tool_type': 'reference_to_video',
        'icon': '📐',
        'badge': 'Seedance Multi-Ref',
        'description': 'توليد مشاهد فيديو مع الاحتفاظ الصارم بهوية الشخصيات وتفاصيل الأزياء من صور مرجعية متعددة.',
        'template': 'studio/tools/reference_to_video.html',
        'model_class': ReferenceToVideoModelConfig,
    },
    'lipsync': {
        'name_ar': 'مزامنة الشفاه السينمائية',
        'name_en': 'Lip Sync',
        'slug': 'lipsync',
        'db_tool_type': 'lipsync',
        'icon': '👄',
        'badge': 'Vidu Precision',
        'description': 'مطابقة حركة شفاه الشخصيات بدقة فائقة مع مسارات الصوت المنطوق بأي لغة.',
        'template': 'studio/tools/lipsync.html',
        'model_class': LipSyncModelConfig,
    },
    'motion-control': {
        'name_ar': 'التحكم الحركي الموجه',
        'name_en': 'Motion Control',
        'slug': 'motion-control',
        'db_tool_type': 'motion_control',
        'icon': '🕺',
        'badge': 'Kling Motion',
        'description': 'نقل حركات الشخصيات والإيماءات المعقدة من فيديو مرجعي إلى أي صورة مستهدفة بدقة مذهلة.',
        'template': 'studio/tools/motion_control.html',
        'model_class': MotionControlModelConfig,
    },
    'avatar-video': {
        'name_ar': 'استوديو الأفاتار المتكلم',
        'name_en': 'Avatar Studio',
        'slug': 'avatar-video',
        'db_tool_type': 'avatar_video',
        'icon': '👤',
        'badge': 'Hedra Character',
        'description': 'إنشاء مقدمي برامج افتراضيين وشخصيات متحدثة بتعبيرات وجه واقعية وتفاعل بشري كامل.',
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
    models_list = model_class.objects.filter(is_active=True) if model_class else []

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
