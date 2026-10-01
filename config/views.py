from django.shortcuts import render
from django.contrib.auth import get_user_model
from apps.billing.models import Plan
from apps.history.models import GenerationHistory
from apps.tools.tts.models import TtsModelConfig, TtsVoice
from apps.tools.text_to_video.models import TextToVideoModelConfig
from apps.tools.text_to_image.models import TextToImageModelConfig

User = get_user_model()


def home(request):
    """Render the official nexmediaai luxury landing page with dynamic plans."""
    plans = Plan.objects.filter(is_deleted=False).order_by('price_usd')
    return render(request, 'home.html', {'plans': plans})


def studio(request):
    """Render the Unified AI Generation Studio with live wallet and tools."""
    user = request.user
    if not user.is_authenticated:
        user = User.objects.filter(is_superuser=True).first()

    context = {
        'active_user': user,
        'tts_models': TtsModelConfig.objects.filter(is_active=True),
        'tts_voices': TtsVoice.objects.filter(is_active=True),
        'video_models': TextToVideoModelConfig.objects.filter(is_active=True),
        'image_models': TextToImageModelConfig.objects.filter(is_active=True),
        'recent_history': GenerationHistory.objects.filter(user=user).order_by('-created_at')[:8] if user else [],
    }
    return render(request, 'studio.html', context)
