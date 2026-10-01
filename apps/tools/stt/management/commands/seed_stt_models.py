from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.tools.stt.models import SttModelConfig


class Command(BaseCommand):
    help = 'Seeds the unified official OpenAI Whisper Speech-to-Text model with minute-based pricing'

    def handle(self, *args, **options):
        models_data = [
            {
                'name': 'Whisper Speech-to-Text',
                'model_id': 'whisper-1',
                'provider': 'OpenAI',
                'pricing_type': 'per_minute',
                'min_duration_seconds': 1,
                'max_duration_seconds': 3600,
                'cost_per_minute': Decimal('1.0000'),
                'cost_per_second': Decimal('0.0167'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
                'sort_order': 1,
            },
        ]

        count = 0
        for m_data in models_data:
            existing = SttModelConfig.objects.filter(model_id=m_data['model_id']).first()
            if existing:
                SttModelConfig.objects.filter(id=existing.id).update(**m_data)
            else:
                SttModelConfig.objects.create(**m_data)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} official OpenAI Whisper model!"))
