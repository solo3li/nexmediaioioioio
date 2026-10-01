import json
import uuid
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django_q.tasks import async_task
from .models import GenerationHistory

User = get_user_model()


def get_active_user(request):
    """Retrieve authenticated user or fallback to system admin for demo interactions."""
    if request.user.is_authenticated:
        return request.user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user, _ = User.objects.get_or_create(
            username='demo_creator',
            defaults={
                'full_name': 'مستخدم تجريبي',
                'standard_credits': Decimal('100.0000'),
                'premium_credits': Decimal('20.0000'),
            }
        )
    return admin_user


@csrf_exempt
@require_http_methods(["POST"])
def generate_api(request):
    """
    Submits an AI generation job across any of the 9 tools,
    deducts user credits, persists GenerationHistory, and dispatches to django-q2.
    """
    user = get_active_user(request)

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    else:
        data = request.POST.dict()

    tool_type = data.get('tool_type', 'text_to_image')
    prompt = data.get('prompt', '').strip()
    model_identifier = data.get('model') or data.get('model_id') or data.get('model_name')
    options = {k: v for k, v in data.items() if k not in ['prompt', 'tool_type']}

    if not prompt:
        return JsonResponse({'status': 'error', 'message': 'يرجى كتابة وصف أو أمر التوليد (Prompt)'}, status=400)

    # Dynamic pricing from tool settings
    from apps.tools.text_to_video.models import TextToVideoModelConfig
    from apps.tools.image_to_video.models import ImageToVideoModelConfig
    from apps.tools.text_to_image.models import TextToImageModelConfig
    from apps.tools.reference_to_video.models import ReferenceToVideoModelConfig
    from apps.tools.lipsync.models import LipSyncModelConfig
    from apps.tools.avatar_video.models import AvatarVideoModelConfig
    from apps.tools.motion_control.models import MotionControlModelConfig
    from apps.tools.stt.models import SttModelConfig
    from apps.tools.tts.models import TtsModelConfig
    standard_cost = Decimal('4.0000')
    premium_cost = Decimal('0.0000')
    model_name = model_identifier or 'Standard Model'

    if tool_type == 'text_to_video':
        cfg = TextToVideoModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TextToVideoModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TextToVideoModelConfig.objects.filter(is_default=True, is_active=True).first() or TextToVideoModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '1080p')).lower()
            try:
                duration = int(data.get('duration', cfg.default_duration))
            except (ValueError, TypeError):
                duration = cfg.default_duration

            # Automatic backend mapping for discrete models to ensure 100% Crun AI compatibility
            api_duration = duration
            if cfg.duration_type == 'discrete':
                valid_durations = cfg.get_durations_list()
                if valid_durations and duration not in valid_durations:
                    api_duration = min(valid_durations, key=lambda x: abs(x - duration))
            options['api_duration'] = api_duration
            options['requested_duration'] = duration

            if '480' in res:
                rate = cfg.cost_480p
            elif '720' in res:
                rate = cfg.cost_720p
            elif '4k' in res:
                rate = cfg.cost_4k
            else:
                rate = cfg.cost_1080p

            if cfg.pricing_type == 'per_second':
                calc_cost = rate * Decimal(duration)
            else:
                calc_cost = rate

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'image_to_video':
        cfg = ImageToVideoModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = ImageToVideoModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = ImageToVideoModelConfig.objects.filter(is_default=True, is_active=True).first() or ImageToVideoModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '1080p')).lower()
            try:
                duration = int(data.get('duration', cfg.default_duration))
            except (ValueError, TypeError):
                duration = cfg.default_duration

            # Automatic backend mapping for discrete models to ensure 100% Crun AI compatibility
            api_duration = duration
            if cfg.duration_type == 'discrete':
                valid_durations = cfg.get_durations_list()
                if valid_durations and duration not in valid_durations:
                    api_duration = min(valid_durations, key=lambda x: abs(x - duration))
            options['api_duration'] = api_duration
            options['requested_duration'] = duration

            if '480' in res:
                rate = cfg.cost_480p
            elif '720' in res:
                rate = cfg.cost_720p
            elif '4k' in res:
                rate = cfg.cost_4k
            else:
                rate = cfg.cost_1080p

            if cfg.pricing_type == 'per_second':
                calc_cost = rate * Decimal(duration)
            else:
                calc_cost = rate

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'text_to_image':
        cfg = TextToImageModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TextToImageModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TextToImageModelConfig.objects.filter(is_default=True, is_active=True).first() or TextToImageModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '1k')).lower()
            try:
                num_images = int(data.get('num_images', 1))
                if num_images not in [1, 2, 4]:
                    num_images = 1
            except (ValueError, TypeError):
                num_images = 1
            options['num_images'] = num_images
            options['resolution'] = res

            rate = cfg.get_cost_for_resolution(res)
            calc_cost = rate * Decimal(num_images)

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'reference_to_video':
        cfg = ReferenceToVideoModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = ReferenceToVideoModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = ReferenceToVideoModelConfig.objects.filter(is_default=True, is_active=True).first() or ReferenceToVideoModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '1080p')).lower()
            try:
                duration = int(data.get('duration', cfg.default_duration))
            except (ValueError, TypeError):
                duration = cfg.default_duration

            api_duration = duration
            if cfg.duration_type == 'discrete':
                valid_durations = cfg.get_durations_list()
                if valid_durations and duration not in valid_durations:
                    api_duration = min(valid_durations, key=lambda x: abs(x - duration))
            options['api_duration'] = api_duration
            options['requested_duration'] = duration

            if '480' in res:
                rate = cfg.cost_480p
            elif '720' in res:
                rate = cfg.cost_720p
            elif '4k' in res:
                rate = cfg.cost_4k
            else:
                rate = cfg.cost_1080p

            if cfg.pricing_type == 'per_second':
                calc_cost = rate * Decimal(duration)
            else:
                calc_cost = rate

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'lipsync':
        cfg = LipSyncModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = LipSyncModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = LipSyncModelConfig.objects.filter(is_default=True, is_active=True).first() or LipSyncModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '1080p')).lower()
            try:
                duration = int(data.get('duration', cfg.default_duration))
            except (ValueError, TypeError):
                duration = cfg.default_duration

            api_duration = duration
            if cfg.duration_type == 'discrete':
                valid_durations = cfg.get_durations_list()
                if valid_durations and duration not in valid_durations:
                    api_duration = min(valid_durations, key=lambda x: abs(x - duration))
            options['api_duration'] = api_duration
            options['requested_duration'] = duration

            if '480' in res:
                rate = cfg.cost_480p
            elif '720' in res:
                rate = cfg.cost_720p
            elif '4k' in res:
                rate = cfg.cost_4k
            else:
                rate = cfg.cost_1080p

            if cfg.pricing_type == 'per_second':
                calc_cost = rate * Decimal(duration)
            else:
                calc_cost = rate

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'avatar_video':
        cfg = AvatarVideoModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = AvatarVideoModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = AvatarVideoModelConfig.objects.filter(is_default=True, is_active=True).first() or AvatarVideoModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '720p')).lower()
            try:
                duration = int(data.get('duration', cfg.min_duration))
            except (ValueError, TypeError):
                duration = cfg.min_duration

            duration = max(cfg.min_duration, min(duration, cfg.max_duration))
            options['duration'] = duration
            options['requested_duration'] = duration

            calc_cost = cfg.calculate_total_cost(res, duration)

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'motion_control':
        cfg = MotionControlModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = MotionControlModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = MotionControlModelConfig.objects.filter(is_default=True, is_active=True).first() or MotionControlModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            res = str(data.get('resolution', '720p')).lower()
            try:
                duration = int(data.get('duration', cfg.min_duration))
            except (ValueError, TypeError):
                duration = cfg.min_duration

            duration = max(cfg.min_duration, min(duration, cfg.max_duration))
            options['duration'] = duration
            options['requested_duration'] = duration

            calc_cost = cfg.calculate_total_cost(res, duration)

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'stt':
        cfg = SttModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = SttModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = SttModelConfig.objects.filter(is_default=True, is_active=True).first() or SttModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            try:
                duration = int(data.get('duration', 60))
            except (ValueError, TypeError):
                duration = 60

            duration = max(cfg.min_duration_seconds, min(duration, cfg.max_duration_seconds))
            options['duration'] = duration
            options['requested_duration'] = duration

            calc_cost = cfg.calculate_total_cost(duration)

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    elif tool_type == 'tts':
        cfg = TtsModelConfig.objects.filter(model_id=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TtsModelConfig.objects.filter(name=model_identifier, is_active=True).first()
        if not cfg:
            cfg = TtsModelConfig.objects.filter(is_default=True, is_active=True).first() or TtsModelConfig.objects.first()

        if cfg:
            model_name = cfg.name
            char_count = len(prompt or '')
            quality_mode = str(data.get('quality', data.get('quality_tier', cfg.quality_tier))).lower()
            options['char_count'] = char_count
            options['quality_mode'] = quality_mode

            calc_cost = cfg.calculate_total_cost(char_count, quality_mode)

            if cfg.allowed_wallet == 'premium':
                premium_cost = calc_cost
                standard_cost = Decimal('0.0000')
            else:
                standard_cost = calc_cost

    else:
        # Fallback COST_MAP for other tools until updated
        COST_MAP = {
            'text_to_image': Decimal('4.0000'),
            'image_to_video': Decimal('5.0000'),
            'reference_to_video': Decimal('20.0000'),
            'lipsync': Decimal('3.0000'),
            'motion_control': Decimal('10.0000'),
            'tts': Decimal('1.0000'),
            'stt': Decimal('1.5000'),
            'avatar_video': Decimal('6.0000'),
        }
        standard_cost = COST_MAP.get(tool_type, Decimal('4.0000'))
        if tool_type in ['reference_to_video']:
            premium_cost = Decimal('1.0000')

    # Verify and deduct balance
    if not user.has_sufficient_balance(standard_cost, premium_cost):
        return JsonResponse({
            'status': 'error',
            'message': 'رصيد المحفظة غير كافٍ لإتمام التوليد، يرجى ترقية باقتك أو شحن الرصيد.',
            'standard_credits': float(user.standard_credits),
            'premium_credits': float(user.premium_credits)
        }, status=402)

    deducted = user.deduct_credits(standard_cost, premium_cost)
    if not deducted:
        return JsonResponse({'status': 'error', 'message': 'تعذر خصم الرصيد حالياً، حاول مجدداً.'}, status=500)

    task_uuid = str(uuid.uuid4())

    history = GenerationHistory.objects.create(
        user=user,
        tool_type=tool_type,
        model_name=model_name,
        prompt=prompt,
        standard_credits_cost=standard_cost,
        premium_credits_cost=premium_cost,
        meta_info=options,
        status='pending',
        task_id=task_uuid
    )

    # Dispatch to background task queue
    async_task('apps.history.tasks.process_generation_task', history.id)

    return JsonResponse({
        'status': 'success',
        'history_id': history.id,
        'task_id': task_uuid,
        'standard_credits_left': float(user.standard_credits),
        'premium_credits_left': float(user.premium_credits),
        'message': 'تم إرسال مهمة التوليد إلى طابور المعالجة بنجاح'
    })


@require_http_methods(["GET"])
def generation_status_api(request, history_id):
    """Polls real-time state of an ongoing or completed generation task."""
    try:
        history = GenerationHistory.objects.get(id=history_id)
        return JsonResponse({
            'status': history.status,
            'tool_type': history.tool_type,
            'duration_seconds': history.duration_seconds,
            'result_url': history.result_url,
            'thumbnail_url': history.thumbnail_url,
            'error_message': history.error_message,
        })
    except GenerationHistory.DoesNotExist:
        return JsonResponse({'status': 'not_found', 'message': 'Job not found'}, status=404)


@require_http_methods(["GET"])
def user_history_api(request):
    """Retrieves recent user generations for the gallery drawer."""
    user = get_active_user(request)
    recent_jobs = GenerationHistory.objects.filter(user=user).order_by('-created_at')[:15]
    items = []
    for j in recent_jobs:
        items.append({
            'id': j.id,
            'tool_type': j.get_tool_type_display(),
            'model_name': j.model_name,
            'prompt': j.prompt,
            'status': j.status,
            'result_url': j.result_url,
            'thumbnail_url': j.thumbnail_url,
            'duration_seconds': j.duration_seconds,
            'created_at': j.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'status': 'success', 'history': items})
