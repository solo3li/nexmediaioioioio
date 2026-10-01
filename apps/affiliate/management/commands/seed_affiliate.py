from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.affiliate.models import AffiliateSettings


class Command(BaseCommand):
    help = 'Seeds initial affiliate settings'

    def handle(self, *args, **options):
        obj, created = AffiliateSettings.objects.get_or_create(
            id=1,
            defaults={
                'attribution_period_days': 30,
                'hold_period_days': 14,
                'first_purchase_rate': Decimal('20.00'),
                'recurring_rate': Decimal('10.00'),
                'max_package_duration_days': 365,
                'min_payout_usd': Decimal('50.00'),
                'min_payout_egp': Decimal('1000.00'),
                'is_program_active': True,
            }
        )
        status = 'Created' if created else 'Already exists'
        self.stdout.write(self.style.SUCCESS(f'{status} Affiliate Settings (30d attribution, 14d hold).'))
