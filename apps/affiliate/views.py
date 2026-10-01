from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import AffiliateProfile, AffiliatePayout, AffiliateSettings


@login_required
def affiliate_dashboard_view(request):
    profile, _ = AffiliateProfile.objects.get_or_create(
        user=request.user,
        defaults={'referral_code': request.user.username.upper(), 'is_active': True}
    )
    settings_obj = AffiliateSettings.get_settings()
    host = request.build_absolute_uri('/')[:-1]
    referral_url = f"{host}/?ref={profile.referral_code}"

    # Handle Payout Request
    if request.method == 'POST' and request.POST.get('action') == 'request_payout':
        currency = request.POST.get('currency', 'USD').upper()
        payout_method = request.POST.get('payout_method', '').strip()
        payout_account = request.POST.get('payout_account', '').strip()
        affiliate_message = request.POST.get('affiliate_message', '').strip()
        
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except Exception:
            amount = Decimal('0')

        available = profile.available_usd if currency == 'USD' else profile.available_egp
        min_payout = settings_obj.min_payout_usd if currency == 'USD' else settings_obj.min_payout_egp

        if amount <= Decimal('0'):
            messages.error(request, 'يرجى إدخال مبلغ سحب صحيح أكبر من الصفر.')
        elif amount < min_payout:
            messages.error(request, f'الحد الأدنى لطلب السحب هو {min_payout} {currency}.')
        elif amount > available:
            messages.error(request, f'المبلغ المطلوب ({amount} {currency}) يتجاوز رصيدك المتاح للسحب ({available} {currency}).')
        elif not payout_method or not payout_account:
            messages.error(request, 'يرجى اختيار طريقة السحب وتدوين بيانات الحساب/المحفظة.')
        else:
            AffiliatePayout.objects.create(
                affiliate_profile=profile,
                amount=amount,
                currency=currency,
                payout_method=payout_method,
                payout_account=payout_account,
                affiliate_message=affiliate_message,
                status='PENDING',
            )
            messages.success(request, f'تم إرسال طلب سحب بقيمة {amount} {currency} بنجاح! سيتم التنفيذ خلال 24 ساعة.')
            return redirect('affiliate_dashboard')

    # Aggregates
    referrals_count = profile.referrals.count()
    converted_count = profile.referrals.filter(has_converted=True).count()
    commissions = profile.commissions.select_related('customer', 'plan').order_by('-created_at')[:30]
    payouts = profile.payouts.order_by('-requested_at')[:15]

    return render(request, 'affiliate/dashboard.html', {
        'profile': profile,
        'referral_url': referral_url,
        'settings': settings_obj,
        'referrals_count': referrals_count,
        'converted_count': converted_count,
        'commissions': commissions,
        'payouts': payouts,
    })
