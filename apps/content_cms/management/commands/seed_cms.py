from django.core.management.base import BaseCommand
from apps.content_cms.models import CustomPage, BlogPost, SystemAnnouncement


class Command(BaseCommand):
    help = 'Seeds initial CMS content (pages, announcements, and welcome blog post)'

    def handle(self, *args, **options):
        # 1. Terms of Service
        CustomPage.objects.update_or_create(
            slug='terms',
            defaults={
                'title_en': 'Terms of Service',
                'title_ar': 'شروط الخدمة والاتفاقية',
                'content_en': 'Welcome to NexMedia. By using our generative AI media platform, you agree to comply with our fair use policies, respect intellectual property, and adhere to our acceptable usage standards.',
                'content_ar': 'أهلاً بكم في نيكس ميديا (NexMedia). باستخدامك لمنصتنا لإنتاج الوسائط بالذكاء الاصطناعي، فإنك توافق على الالتزام بسياسات الاستخدام العادل واحترام حقوق الملكية الفكرية.',
                'is_active': True,
            }
        )

        # 2. Privacy Policy
        CustomPage.objects.update_or_create(
            slug='privacy',
            defaults={
                'title_en': 'Privacy Policy',
                'title_ar': 'سياسة الخصوصية وحماية البيانات',
                'content_en': 'NexMedia takes your privacy seriously. We employ enterprise-grade encryption and secure cloud infrastructure to ensure that your generated prompts and media assets remain strictly confidential and protected.',
                'content_ar': 'تولي نيكس ميديا أهمية قصوى لخصوصيتك وبياناتك. نحن نوفر تشفيراً متقدماً وبنية سحابية آمنة تضمن سرية مدخلاتك ووسائطك المولدة.',
                'is_active': True,
            }
        )

        # 3. About Us
        CustomPage.objects.update_or_create(
            slug='about',
            defaults={
                'title_en': 'About NexMedia',
                'title_ar': 'عن منصة نيكس ميديا',
                'content_en': 'NexMedia is a premier Royal Andalusian-inspired generative AI creative suite, empowering artists, creators, and enterprises with world-class neural models for voice, video, and imagery.',
                'content_ar': 'نيكس ميديا هي منصة إبداعية متكاملة بالذكاء الاصطناعي مستوحاة من فخامة الطراز الأندلسي، تمكّن الفنانين وصنّاع المحتوى والشركات من إنتاج الفيديو والصوت والصور بأحدث النماذج العصبية العالمية.',
                'is_active': True,
            }
        )

        # 4. Contact Us
        CustomPage.objects.update_or_create(
            slug='contact',
            defaults={
                'title_en': 'Contact Concierge',
                'title_ar': 'تواصل معنا والدعم الملكي',
                'content_en': 'Have inquiries, custom enterprise requirements, or need dedicated support? Reach out to our concierge team at support@nexmedia.io.',
                'content_ar': 'هل لديك استفسارات أو متطلبات خاصة بالمؤسسات أو تحتاج لدعم خاص؟ تواصل مع فريق الدعم لدينا عبر support@nexmedia.io.',
                'is_active': True,
            }
        )

        # 5. Announcement
        SystemAnnouncement.objects.update_or_create(
            title_en='Welcome to NexMedia Royal Studio',
            defaults={
                'title_ar': 'مرحباً بكم في استوديو نيكس ميديا الأندلسي',
                'message_en': 'Experience state-of-the-art cinematic video and voice synthesis powered by Kling, Veo, and ElevenLabs.',
                'message_ar': 'استمتع بأحدث تقنيات توليد الفيديو السينمائي والأصوات الطبيعية المدعومة بأحدث النماذج.',
                'banner_type': 'info',
                'is_active': True,
            }
        )

        # 6. Welcome Blog Post
        BlogPost.objects.update_or_create(
            slug='welcome-to-the-future-of-creative-ai',
            defaults={
                'category': 'Platform',
                'title_en': 'The Dawn of Royal AI Media: Introducing NexMedia',
                'title_ar': 'فجر الإعلام الاصطناعي الراقي: إطلاق منصة نيكس ميديا',
                'content_en': 'We are thrilled to unveil NexMedia, uniting high-fidelity multi-model synthesis under an Andalusian-crafted luxury creative suite.',
                'content_ar': 'يسرنا إطلاق منصة نيكس ميديا، التي تجمع بين أحدث نماذج التوليد الفائق للصوت والفيديو والصورة في بيئة إبداعية مستوحاة من الفخامة الأندلسية.',
                'is_published': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded CMS pages, announcement, and welcome blog post!'))
