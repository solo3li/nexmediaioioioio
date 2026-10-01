from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.billing.models import Plan


class Command(BaseCommand):
    help = 'Seeds standard subscription plans replicating NexClone production tiers'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Free Trial',
                'name_ar': 'تجربة مجانية',
                'description': 'Free welcome trial credits for new users',
                'description_ar': 'رصيد تجريبي ترحيبي للأعضاء الجدد لتجربة المنظومة',
                'features': '15 Standard Credits\n5 Premium Credits\nStandard Quality Models\nCommunity Support',
                'features_ar': '15 رصيد قياسي\n5 رصيد مميز\nنماذج الجودة القياسية\nدعم مجتمعي',
                'duration_days': 7,
                'grace_period_days': 0,
                'price_usd': Decimal('0.00'),
                'price_egp': Decimal('0.00'),
                'standard_credits': Decimal('15.0000'),
                'premium_credits': Decimal('5.0000'),
                'is_free_trial': True,
                'is_default_registration_plan': True,
            },
            {
                'name': 'Basic Monthly',
                'name_ar': 'أساسي شهري',
                'description': 'Ideal for creators and hobbyists exploring AI audio and visual tools',
                'description_ar': 'مثالي للمبدعين والهواة لاستكشاف أدوات الصوتيات والبصريات',
                'features': '100 Standard Credits\n10 Premium Credits\nAll 8 AI Tools Enabled\nLossless Audio & HD Video',
                'features_ar': '100 رصيد قياسي\n10 رصيد مميز\nتفعيل البوابات الثمانية\nصوت فائق الدقة وفيديو عالي الجودة',
                'duration_days': 30,
                'grace_period_days': 3,
                'price_usd': Decimal('10.00'),
                'price_egp': Decimal('500.00'),
                'standard_credits': Decimal('100.0000'),
                'premium_credits': Decimal('10.0000'),
                'affiliate_first_commission_type': 'Percentage',
                'affiliate_first_commission_value_usd': Decimal('20.00'),
                'affiliate_first_commission_value_egp': Decimal('20.00'),
                'affiliate_recurring_commission_type': 'Percentage',
                'affiliate_recurring_commission_value_usd': Decimal('10.00'),
                'affiliate_recurring_commission_value_egp': Decimal('10.00'),
            },
            {
                'name': 'Pro Quarterly',
                'name_ar': 'احترافي ربع سنوي',
                'description': 'For professional creators and small studios needing higher throughput',
                'description_ar': 'لصناع المحتوى المحترفين والاستوديوهات الصغيرة لاستهلاك منتظم',
                'features': '350 Standard Credits\n40 Premium Credits\nFast Priority Queue\n4K Neural Video & Studio Audio',
                'features_ar': '350 رصيد قياسي\n40 رصيد مميز\nأولوية متقدمة في طابور المعالجة\nفيديو 4K عصبي وهندسة صوت احترافية',
                'duration_days': 90,
                'grace_period_days': 5,
                'price_usd': Decimal('25.00'),
                'price_egp': Decimal('1200.00'),
                'standard_credits': Decimal('350.0000'),
                'premium_credits': Decimal('40.0000'),
                'affiliate_first_commission_type': 'Fixed',
                'affiliate_first_commission_value_usd': Decimal('10.00'),
                'affiliate_first_commission_value_egp': Decimal('400.00'),
                'affiliate_recurring_commission_type': 'Percentage',
                'affiliate_recurring_commission_value_usd': Decimal('15.00'),
                'affiliate_recurring_commission_value_egp': Decimal('15.00'),
            },
            {
                'name': 'Elite Semi-Annual',
                'name_ar': 'نخبة نصف سنوي',
                'description': 'High-volume production tier with extended storage and priority GPUs',
                'description_ar': 'باقة الإنتاج الضخم بسعات تخزين موسعة ومعالجات ذات أولوية عليا',
                'features': '800 Standard Credits\n100 Premium Credits\nTop Tier Processing Priority\nMinIO Cloud Storage 50GB',
                'features_ar': '800 رصيد قياسي\n100 رصيد مميز\nأعلى أولوية معالجة فورية\nمساحة تخزين سحابية 50 جيجابايت',
                'duration_days': 180,
                'grace_period_days': 7,
                'price_usd': Decimal('45.00'),
                'price_egp': Decimal('2200.00'),
                'standard_credits': Decimal('800.0000'),
                'premium_credits': Decimal('100.0000'),
                'affiliate_first_commission_type': 'Fixed',
                'affiliate_first_commission_value_usd': Decimal('20.00'),
                'affiliate_first_commission_value_egp': Decimal('900.00'),
                'affiliate_recurring_commission_type': 'Fixed',
                'affiliate_recurring_commission_value_usd': Decimal('5.00'),
                'affiliate_recurring_commission_value_egp': Decimal('250.00'),
            },
            {
                'name': 'Ultimate Annual',
                'name_ar': 'ألتيميت سنوي',
                'description': 'Maximum power, dedicated concurrency, and unlimited potential',
                'description_ar': 'القوة القصوى مع تزامن معالجة مخصص ودعم VIP مباشر',
                'features': '2000 Standard Credits\n300 Premium Credits\nDedicated Concurrency\nVIP Direct Support & Custom Voice Cloning',
                'features_ar': '2000 رصيد قياسي\n300 رصيد مميز\nقنوات معالجة متزامنة مخصصة\nدعم VIP مخصص واستنساخ نبرات صوتية حصرية',
                'duration_days': 365,
                'grace_period_days': 14,
                'price_usd': Decimal('80.00'),
                'price_egp': Decimal('4000.00'),
                'standard_credits': Decimal('2000.0000'),
                'premium_credits': Decimal('300.0000'),
                'affiliate_first_commission_type': 'Fixed',
                'affiliate_first_commission_value_usd': Decimal('40.00'),
                'affiliate_first_commission_value_egp': Decimal('1800.00'),
                'affiliate_recurring_commission_type': 'Fixed',
                'affiliate_recurring_commission_value_usd': Decimal('10.00'),
                'affiliate_recurring_commission_value_egp': Decimal('500.00'),
            },
        ]

        count = 0
        for plan_dict in plans_data:
            plan, created = Plan.objects.update_or_create(
                name=plan_dict['name'],
                defaults=plan_dict
            )
            count += 1
            status_text = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f"{status_text} plan: {plan.name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} plans."))
