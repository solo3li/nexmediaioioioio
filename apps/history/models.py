from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


class GenerationHistory(models.Model):
    """
    Unified Generation History across all 8+ AI tools.
    Stores metadata, media URLs on MinIO S3, credit cost, and execution duration.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    TOOL_CHOICES = [
        ('tts', 'Text to Voice'),
        ('stt', 'Voice to Text'),
        ('text_to_video', 'Text to Video'),
        ('image_to_video', 'Image to Video'),
        ('reference_to_video', 'Reference to Video'),
        ('lipsync', 'Lip Sync'),
        ('motion_control', 'Motion Control'),
        ('text_to_image', 'Text to Image'),
        ('avatar_video', 'Avatar to Video'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generations')
    tool_type = models.CharField(max_length=50, choices=TOOL_CHOICES, db_index=True)
    model_name = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', db_index=True)

    prompt = models.TextField(blank=True, null=True)
    result_url = models.URLField(max_length=1000, blank=True, null=True, help_text="MinIO S3 Presigned URL")
    thumbnail_url = models.URLField(max_length=1000, blank=True, null=True)
    input_file_url = models.URLField(max_length=1000, blank=True, null=True)

    # Credits cost incurred
    standard_credits_cost = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_cost = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))

    duration_seconds = models.FloatField(default=0.0)
    meta_info = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="Async Queue Task ID")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Generation History'
        verbose_name_plural = 'Generation Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_tool_type_display()} ({self.status}) [{self.created_at.strftime('%Y-%m-%d %H:%M')}]"
