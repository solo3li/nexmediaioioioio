from django.contrib import admin
from .models import GenerationHistory


@admin.register(GenerationHistory)
class GenerationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool_type', 'model_name', 'status', 'standard_credits_cost', 'premium_credits_cost', 'duration_seconds', 'created_at')
    list_filter = ('tool_type', 'status')
    search_fields = ('user__username', 'user__email', 'model_name', 'prompt', 'task_id')
    readonly_fields = ('created_at',)
