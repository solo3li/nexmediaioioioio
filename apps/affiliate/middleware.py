import uuid
from django.utils import timezone
from .models import AffiliateProfile, AffiliateReferral, AffiliateSettings


class AffiliateReferralMiddleware:
    """
    Captures ?ref= or ?referral= query parameters, creates referral click records,
    and sets a persistent 30-day cookie for attribution upon checkout/registration.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ref_code = request.GET.get('ref') or request.GET.get('referral')
        response = self.get_response(request)

        if ref_code:
            code = ref_code.strip()
            profile = AffiliateProfile.objects.filter(referral_code__iexact=code, is_active=True).first()
            if profile:
                # Avoid counting if visiting their own referral link
                if request.user.is_authenticated and request.user.id == profile.user_id:
                    return response

                # Increment total clicks
                AffiliateProfile.objects.filter(id=profile.id).update(
                    total_clicks=models.F('total_clicks') + 1
                )

                # Cookie session token
                session_token = request.COOKIES.get('nex_ref_token') or uuid.uuid4().hex
                ip_addr = request.META.get('REMOTE_ADDR')

                # Log or update referral record
                AffiliateReferral.objects.create(
                    affiliate_profile=profile,
                    referred_user=request.user if request.user.is_authenticated else None,
                    session_token=session_token,
                    ip_address=ip_addr,
                )

                # Set 30 days cookie
                settings_obj = AffiliateSettings.get_settings()
                max_age = settings_obj.attribution_period_days * 24 * 3600
                response.set_cookie('nex_ref', code, max_age=max_age, httponly=True, samesite='Lax')
                response.set_cookie('nex_ref_token', session_token, max_age=max_age, httponly=True, samesite='Lax')

        return response
