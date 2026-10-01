from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    AffiliateProfile, AffiliateReferral, AffiliateCommission,
    AffiliatePayout, AffiliateSettings
)


class AffiliateService:
    @staticmethod
    def link_user_to_referral(user, ref_code: str = None, session_token: str = None):
        """Links a registered user to their referring affiliate"""
        referral = None
        if ref_code:
            profile = AffiliateProfile.objects.filter(referral_code__iexact=ref_code.strip(), is_active=True).first()
            if profile and profile.user_id != user.id:
                referral = AffiliateReferral.objects.create(
                    affiliate_profile=profile,
                    referred_user=user,
                    session_token=session_token,
                )
                return referral

        if session_token:
            referral = AffiliateReferral.objects.filter(
                session_token=session_token,
                referred_user__isnull=True
            ).order_by('-clicked_at').first()
            if referral and referral.affiliate_profile.user_id != user.id:
                referral.referred_user = user
                referral.save(update_fields=['referred_user'])
                return referral

        return None

    @classmethod
    @transaction.atomic
    def process_payment_commission(cls, payment) -> AffiliateCommission | None:
        """
        Calculates and creates an AffiliateCommission for a successful payment.
        Honors attribution window, hold period, first purchase vs recurring rate,
        and maximum accumulated package days cap.
        """
        settings_obj = AffiliateSettings.get_settings()
        if not settings_obj.is_program_active:
            return None

        # Find referral
        referral = AffiliateReferral.objects.select_for_update().filter(
            referred_user=payment.user
        ).order_by('-clicked_at').first()

        if not referral or not referral.is_attribution_active:
            return None

        # Verify not self-referral
        if referral.affiliate_profile.user_id == payment.user_id:
            return None

        # Determine type (First purchase vs Recurring)
        is_first = not referral.has_converted
        rate = settings_obj.first_purchase_rate if is_first else settings_obj.recurring_rate
        comm_type = 'FIRST_PURCHASE' if is_first else 'RECURRING'

        # Check duration cap
        plan_days = payment.plan.duration_days if payment.plan else 30
        if referral.accumulated_package_days >= settings_obj.max_package_duration_days:
            return None  # Reached commission cap

        # Calculate amount
        comm_amount = (Decimal(str(payment.amount)) * rate) / Decimal('100.00')
        comm_amount = comm_amount.quantize(Decimal('0.01'))

        if comm_amount <= Decimal('0.00'):
            return None

        # Create commission
        hold_days = settings_obj.hold_period_days
        available_at = timezone.now() + timedelta(days=hold_days)

        commission = AffiliateCommission.objects.create(
            affiliate_profile=referral.affiliate_profile,
            referral=referral,
            customer=payment.user,
            plan=payment.plan,
            payment=payment,
            type=comm_type,
            amount=comm_amount,
            currency=payment.currency,
            rate=rate,
            status='PENDING',
            available_at=available_at,
        )

        # Update referral stats
        referral.has_converted = True
        if not referral.first_eligible_payment_at:
            referral.first_eligible_payment_at = timezone.now()
        referral.accumulated_package_days += plan_days
        referral.save(update_fields=['has_converted', 'first_eligible_payment_at', 'accumulated_package_days'])

        return commission

    @classmethod
    def release_hold_period_commissions(cls) -> int:
        """Scheduled job task to release matured commissions from PENDING to AVAILABLE"""
        now = timezone.now()
        updated_count = AffiliateCommission.objects.filter(
            status='PENDING',
            available_at__lte=now
        ).update(status='AVAILABLE')
        return updated_count
