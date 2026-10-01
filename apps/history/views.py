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
                'full_name': 'تجربة الزائر الأندلسي',
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

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)

    tool_type = data.get('tool_type', 'text_to_image')
    model_name = data.get('model_name', 'Grok Imagine HD')
    prompt = data.get('prompt', '').strip()
    options = data.get('options', {})

    if not prompt:
        return JsonResponse({'status': 'error', 'message': 'يرجى كتابة وصف أو أمر التوليد (Prompt)'}, status=400)

    # Cost calculation mapping based on tool
    COST_MAP = {
        'text_to_image': Decimal('4.0000'),
        'text_to_video': Decimal('8.0000'),
        'image_to_video': Decimal('5.0000'),
        'reference_to_video': Decimal('20.0000'),
        'lipsync': Decimal('3.0000'),
        'motion_control': Decimal('10.0000'),
        'tts': Decimal('1.0000'),
        'stt': Decimal('1.5000'),
        'avatar_video': Decimal('6.0000'),
    }

    standard_cost = COST_MAP.get(tool_type, Decimal('4.0000'))
    premium_cost = Decimal('1.0000') if tool_type in ['reference_to_video', 'text_to_video'] else Decimal('0.0000')

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
