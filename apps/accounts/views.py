from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from apps.affiliate.models import AffiliateProfile
from apps.affiliate.services import AffiliateService
from apps.billing.models import Subscription, Payment, Invoice
from .forms import UserRegistrationForm, UserLoginForm
from .models import ApplicationUser, DeviceFingerprint


def register_view(request):
    if request.user.is_authenticated:
        return redirect('studio')

    ref_cookie = request.COOKIES.get('nex_ref', '')
    session_token = request.COOKIES.get('nex_ref_token', '')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Link to affiliate referral
            ref_code = form.cleaned_data.get('referral_code') or ref_cookie
            if ref_code or session_token:
                AffiliateService.link_user_to_referral(
                    user=user,
                    ref_code=ref_code,
                    session_token=session_token
                )

            # Auto-create AffiliateProfile for new user
            AffiliateProfile.objects.get_or_create(
                user=user,
                defaults={'referral_code': user.username.upper(), 'is_active': True}
            )

            # Log device fingerprint if available
            ip = request.META.get('REMOTE_ADDR')
            ua = request.META.get('HTTP_USER_AGENT', '')
            DeviceFingerprint.objects.create(
                user=user,
                device_hash=f"{ip}_{ua[:40]}",
                user_agent=ua,
                ip_address=ip
            )

            login(request, user)
            return redirect('studio')
    else:
        form = UserRegistrationForm(initial={'referral_code': ref_cookie})

    return render(request, 'accounts/register.html', {
        'form': form,
        'has_ref': bool(ref_cookie),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('studio')

    error_message = None
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('studio')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                # Try finding by email
                user_obj = ApplicationUser.objects.filter(email__iexact=username_or_email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                return redirect(next_url)
            else:
                error_message = 'اسم المستخدم أو كلمة المرور غير صحيحة.'
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'error_message': error_message,
        'next': next_url,
    })


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    subscriptions = Subscription.objects.filter(user=user).select_related('plan').order_by('-created_at')
    active_sub = subscriptions.filter(status='active', end_date__gte=timezone.now()).first()
    recent_payments = Payment.objects.filter(user=user).select_related('plan').order_by('-created_at')[:5]

    return render(request, 'accounts/profile.html', {
        'user': user,
        'active_sub': active_sub,
        'subscriptions': subscriptions,
        'recent_payments': recent_payments,
    })
