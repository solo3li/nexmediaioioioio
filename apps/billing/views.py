import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Plan, Payment, ManualPaymentMethod
from .services import BillingService, PaymobService, PayPalService

logger = logging.getLogger(__name__)


@login_required
def checkout_view(request):
    """Initiates checkout with chosen gateway (Paymob, PayPal, or Manual)"""
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        gateway = request.POST.get('gateway', 'paymob').lower()
        method = request.POST.get('method', 'card').lower()
    else:
        plan_id = request.GET.get('plan_id')
        gateway = request.GET.get('gateway', 'paymob').lower()
        method = request.GET.get('method', 'card').lower()

    if not plan_id:
        return redirect('home')

    plan = get_object_or_404(Plan, id=plan_id, is_deleted=False)
    host = request.build_absolute_uri('/')[:-1]

    if gateway == 'paypal':
        result = PayPalService.initiate_payment(request.user, plan, return_host=host)
    elif gateway == 'manual':
        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price_egp if plan.price_egp > 0 else plan.price_usd,
            currency='EGP' if plan.price_egp > 0 else 'USD',
            method='manual',
            status='Pending',
            payment_id=f"MAN-{request.user.id}-{plan.id}"
        )
        return redirect(f"/billing/manual/{payment.id}/")
    else: # Paymob (Card or Mobile Wallet)
        result = PaymobService.initiate_payment(request.user, plan, method=method, return_host=host)

    if result.get('success'):
        return redirect(result['checkout_url'])
    else:
        return render(request, 'billing/error.html', {'error': result.get('ErrorMessage', 'Failed to initialize payment')})


@login_required
def mock_checkout_view(request):
    """
    Simulated Sandbox payment screen with Royal Andalusian styling
    for rapid local development, testing, and automated credit verification.
    """
    payment_id = request.GET.get('payment_id')
    gateway = request.GET.get('gateway', 'paymob')
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            # Complete the payment, activate subscription, grant credits & affiliate commission
            BillingService.activate_subscription_and_grant_credits(payment)
            return redirect(f"/billing/success/?payment_id={payment.id}")
        else:
            payment.status = 'Failed'
            payment.save(update_fields=['status'])
            return redirect(f"/billing/cancel/?payment_id={payment.id}")

    return render(request, 'billing/mock_checkout.html', {
        'payment': payment,
        'plan': payment.plan,
        'gateway': gateway,
    })


@csrf_exempt
def paymob_webhook_view(request):
    """Paymob transaction callback webhook with HMAC verification"""
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        obj = data.get('obj', {})
        success = obj.get('success', False)
        received_hmac = request.GET.get('hmac', '')

        # Verify HMAC
        if received_hmac and not PaymobService.verify_hmac(obj, received_hmac):
            logger.warning("Paymob Webhook HMAC verification failed.")
            return HttpResponse("Invalid HMAC Signature", status=403)

        if success:
            order_data = obj.get('order', {})
            special_ref = order_data.get('special_reference') or obj.get('special_reference')
            # Extract payment ID
            payment = None
            if special_ref and special_ref.startswith('PM_'):
                pid = special_ref.split('_')[1]
                payment = Payment.objects.filter(id=pid, status='Pending').first()

            if not payment:
                # Fallback to order ID matching
                payment = Payment.objects.filter(payment_id=str(obj.get('id')), status='Pending').first()

            if payment:
                BillingService.activate_subscription_and_grant_credits(payment)
                logger.info(f"Paymob Webhook activated Payment #{payment.id}")

        return HttpResponse("OK", status=200)
    except Exception as e:
        logger.error(f"Paymob Webhook error: {e}")
        return HttpResponse("Server Error", status=500)


@csrf_exempt
def paypal_webhook_view(request):
    """PayPal webhook listener"""
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        event_type = payload.get('event_type')

        if event_type in ['CHECKOUT.ORDER.APPROVED', 'PAYMENT.CAPTURE.COMPLETED']:
            resource = payload.get('resource', {})
            order_id = resource.get('id')
            payment = Payment.objects.filter(payment_id=order_id, status='Pending').first()
            if payment:
                BillingService.activate_subscription_and_grant_credits(payment)
                logger.info(f"PayPal Webhook activated Payment #{payment.id}")

        return HttpResponse("OK", status=200)
    except Exception as e:
        logger.error(f"PayPal Webhook error: {e}")
        return HttpResponse("Server Error", status=500)


@login_required
def payment_success_view(request):
    payment_id = request.GET.get('payment_id')
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'billing/success.html', {
        'payment': payment,
        'subscription': payment.subscription,
        'plan': payment.plan,
    })


@login_required
def payment_cancel_view(request):
    payment_id = request.GET.get('payment_id')
    payment = Payment.objects.filter(id=payment_id, user=request.user).first() if payment_id else None
    return render(request, 'billing/cancel.html', {
        'payment': payment,
    })


@login_required
def manual_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    methods = ManualPaymentMethod.objects.filter(is_active=True)

    if request.method == 'POST':
        receipt_url = request.POST.get('receipt_url', '').strip()
        # In a production setup, user can upload file or provide link
        if receipt_url:
            payment.receipt_url = receipt_url
            payment.save(update_fields=['receipt_url'])
            return render(request, 'billing/manual_pending.html', {'payment': payment})

    return render(request, 'billing/manual_payment.html', {
        'payment': payment,
        'methods': methods,
    })


@login_required
def invoices_list_view(request):
    """List of all invoices generated for user payments"""
    invoices = Invoice.objects.filter(user=request.user).select_related('payment', 'payment__plan').order_by('-created_at')
    return render(request, 'billing/invoices_list.html', {
        'invoices': invoices,
    })


@login_required
def invoice_detail_view(request, invoice_id):
    """Printable luxury invoice view"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'payment': invoice.payment,
        'plan': invoice.payment.plan if invoice.payment else None,
    })
