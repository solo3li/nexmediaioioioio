from decimal import Decimal
from django.core.management.base import BaseCommand

from apps.tools.tts.models import TtsModelConfig, TtsVoice, TtsSetting
from apps.tools.stt.models import SttModelConfig, SttSetting
from apps.tools.text_to_video.models import TextToVideoModelConfig, TextToVideoSetting
from apps.tools.image_to_video.models import ImageToVideoModelConfig, ImageToVideoSetting
from apps.tools.reference_to_video.models import ReferenceToVideoModelConfig, ReferenceToVideoSetting
from apps.tools.lipsync.models import LipSyncModelConfig, LipSyncSetting
from apps.tools.motion_control.models import MotionControlModelConfig, MotionControlSetting
from apps.tools.text_to_image.models import TextToImageModelConfig, TextToImageSetting
from apps.tools.avatar_video.models import AvatarVideoModelConfig, AvatarVideoSetting


class Command(BaseCommand):
    help = 'Seeds all default AI tool configurations, models and pricing'

    def handle(self, *args, **options):
        # 1. TTS
        TtsSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_chars': 5000})
        TtsModelConfig.objects.update_or_create(
            model_id='gemini-tts-standard',
            defaults={
                'name': 'Gemini 2.5 Flash Neural TTS',
                'provider': 'Gemini',
                'cost_per_char': Decimal('0.00100'),
                'allowed_wallet': 'standard',
                'is_active': True,
                'is_default': True,
            }
        )
        TtsModelConfig.objects.update_or_create(
            model_id='eleven_turbo_v2_5',
            defaults={
                'name': 'ElevenLabs Multilingual Studio v2.5',
                'provider': 'ElevenLabs',
                'cost_per_char': Decimal('0.00300'),
                'allowed_wallet': 'premium',
                'is_active': True,
                'is_default': False,
            }
        )
        voices = [
            ('fatima-ar', 'فاطمة (فصحى ملكية)', 'Fatima', 'ar-XA', 'Female', 'Gemini'),
            ('omar-ar', 'عمر (وقار إذاعي)', 'Omar', 'ar-XA', 'Male', 'Gemini'),
            ('zayd-sa', 'زيد (لهجة سعودية)', 'Zayd', 'ar-SA', 'Male', 'Gemini'),
            ('layla-eg', 'ليلى (لهجة مصرية)', 'Layla', 'ar-EG', 'Female', 'Gemini'),
            ('sarah-en', 'Sarah (Executive British)', 'Sarah', 'en-GB', 'Female', 'ElevenLabs'),
            ('adam-en', 'Adam (Deep American)', 'Adam', 'en-US', 'Male', 'ElevenLabs'),
        ]
        for v_id, name_ar, name_en, lang, gender, prov in voices:
            TtsVoice.objects.update_or_create(
                voice_id=v_id,
                defaults={
                    'display_name': name_en,
                    'display_name_ar': name_ar,
                    'language_code': lang,
                    'gender': gender,
                    'provider': prov,
                    'is_active': True,
                }
            )

        # 2. STT
        SttSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_file_size_mb': 25, 'max_duration_minutes': 10})
        SttModelConfig.objects.update_or_create(
            model_id='whisper-large-v3',
            defaults={
                'name': 'Whisper Large v3 Lossless',
                'provider': 'Whisper',
                'cost_per_second': Decimal('0.0167'),
                'cost_per_minute': Decimal('1.0000'),
                'allowed_wallet': 'standard',
                'is_active': True,
                'is_default': True,
            }
        )

        # 3. Text to Video
        TextToVideoSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_prompt_length': 1000})
        TextToVideoModelConfig.objects.update_or_create(
            model_id='kling-v1-6',
            defaults={
                'name': 'Kling AI Cinematic v1.6',
                'provider': 'Kling',
                'cost_480p': Decimal('2.40'),
                'cost_720p': Decimal('5.00'),
                'cost_1080p': Decimal('8.00'),
                'cost_4k': Decimal('15.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
            }
        )
        TextToVideoModelConfig.objects.update_or_create(
            model_id='google-veo-2',
            defaults={
                'name': 'Google Veo 2 Ultra',
                'provider': 'Google',
                'cost_480p': Decimal('4.00'),
                'cost_720p': Decimal('8.00'),
                'cost_1080p': Decimal('12.00'),
                'cost_4k': Decimal('20.00'),
                'allowed_wallet': 'premium',
                'is_active': True,
                'is_default': False,
            }
        )

        # 4. Image to Video
        ImageToVideoSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_image_size_mb': 20})
        ImageToVideoModelConfig.objects.update_or_create(
            model_id='kling-i2v-v1-6',
            defaults={
                'name': 'Kling Image2Video Pro',
                'provider': 'Kling',
                'cost_per_second': Decimal('5.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
            }
        )

        # 5. Reference to Video
        ReferenceToVideoSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_reference_images': 3})
        ReferenceToVideoModelConfig.objects.update_or_create(
            model_id='seedance-r2v-v1',
            defaults={
                'name': 'Seedance Multi-Reference Pro',
                'provider': 'Seedance',
                'cost_per_generation': Decimal('20.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
            }
        )

        # 6. Lip Sync
        LipSyncSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_video_size_mb': 100, 'max_audio_size_mb': 25, 'max_duration_seconds': 120})
        LipSyncModelConfig.objects.update_or_create(
            model_id='vidu-lipsync-pro',
            defaults={
                'name': 'Vidu Neural LipSync Pro',
                'provider': 'Vidu',
                'cost_per_second': Decimal('0.50'),
                'allowed_wallet': 'standard',
                'is_active': True,
                'is_default': True,
            }
        )

        # 7. Motion Control
        MotionControlSetting.objects.get_or_create(id=1, defaults={'is_enabled': True})
        MotionControlModelConfig.objects.update_or_create(
            model_id='kling-motion-control',
            defaults={
                'name': 'Kling Motion Precision v1',
                'provider': 'Kling',
                'base_cost': Decimal('20.00'),
                'cost_per_second': Decimal('2.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
            }
        )

        # 8. Text to Image
        TextToImageSetting.objects.get_or_create(id=1, defaults={'is_enabled': True})
        TextToImageModelConfig.objects.update_or_create(
            model_id='grok-imagine',
            defaults={
                'name': 'Grok Imagine HD',
                'provider': 'Grok',
                'cost_per_image': Decimal('4.00'),
                'allowed_wallet': 'standard',
                'is_active': True,
                'is_default': True,
            }
        )
        TextToImageModelConfig.objects.update_or_create(
            model_id='imagen-3-pro',
            defaults={
                'name': 'Google Imagen 3 Ultra',
                'provider': 'Google',
                'cost_per_image': Decimal('5.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': False,
            }
        )

        # 9. Avatar to Video
        AvatarVideoSetting.objects.get_or_create(id=1, defaults={'is_enabled': True, 'max_audio_duration_seconds': 120})
        AvatarVideoModelConfig.objects.update_or_create(
            model_id='hedra-char-1',
            defaults={
                'name': 'Hedra Character Studio v1',
                'provider': 'Hedra',
                'cost_per_second': Decimal('1.00'),
                'allowed_wallet': 'both',
                'is_active': True,
                'is_default': True,
            }
        )

        self.stdout.write(self.style.SUCCESS("All 9 AI tools, models, voices and default settings seeded successfully!"))
