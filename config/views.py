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
    """Redirect to the active modular AI Generation Studio."""
    from django.shortcuts import redirect
    return redirect('studio_tool', tool_slug='text-to-video')


def set_language_view(request):
    """Switch site language seamlessly between Arabic and English."""
    from django.utils import translation
    from django.conf import settings
    from django.http import HttpResponseRedirect
    
    lang_code = request.GET.get('language') or request.POST.get('language') or 'ar'
    next_url = request.GET.get('next') or request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    
    valid_langs = [code for code, _ in getattr(settings, 'LANGUAGES', [('ar', 'Arabic'), ('en', 'English')])]
    if lang_code in valid_langs:
        translation.activate(lang_code)
        response = HttpResponseRedirect(next_url)
        cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
        response.set_cookie(cookie_name, lang_code, max_age=365 * 24 * 60 * 60, samesite='Lax')
        if hasattr(request, 'session'):
            request.session['_language'] = lang_code
        return response
    return HttpResponseRedirect(next_url)

