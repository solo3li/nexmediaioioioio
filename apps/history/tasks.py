import time
from decimal import Decimal
from django.utils import timezone
from .models import GenerationHistory


def process_generation_task(history_id: int):
    """
    Asynchronous task executed by django-q2 cluster.
    Simulates high-end AI neural pipeline generation and records media artifacts.
    """
    try:
        history = GenerationHistory.objects.get(id=history_id)
        history.status = 'processing'
        history.save(update_fields=['status'])

        # Simulated AI computation latency based on tool type
        start_time = time.time()
        simulated_delay = 3.5 if 'video' in history.tool_type else 2.0
        time.sleep(simulated_delay)

        elapsed = round(time.time() - start_time, 2)
        history.duration_seconds = elapsed

        # Assign realistic sample results based on tool type
        if history.tool_type == 'text_to_image':
            history.result_url = 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1200&q=80'
            history.thumbnail_url = history.result_url
        elif 'video' in history.tool_type:
            history.result_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
            history.thumbnail_url = 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=800&q=80'
        elif history.tool_type in ['tts', 'stt']:
            history.result_url = 'https://actions.google.com/sounds/v1/water/rain_heavy.ogg'
            history.thumbnail_url = ''
        else:
            history.result_url = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80'

        history.status = 'completed'
        history.save(update_fields=['status', 'duration_seconds', 'result_url', 'thumbnail_url'])
        return f"History {history_id} completed successfully in {elapsed}s"

    except GenerationHistory.DoesNotExist:
        return f"History {history_id} not found"
    except Exception as e:
        if 'history' in locals() and history:
            history.status = 'failed'
            history.error_message = str(e)
            history.save(update_fields=['status', 'error_message'])
        return f"History {history_id} error: {str(e)}"
