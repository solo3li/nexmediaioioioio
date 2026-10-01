from django.core.management.base import BaseCommand
from apps.affiliate.services import AffiliateService


class Command(BaseCommand):
    help = 'Releases affiliate commissions whose 14-day hold period has passed'

    def handle(self, *args, **options):
        released = AffiliateService.release_hold_period_commissions()
        self.stdout.write(self.style.SUCCESS(f'Released {released} commissions to AVAILABLE status.'))
