import hashlib
import hmac
import json
import logging
import urllib.request
import urllib.error
import uuid
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import ApplicationUser
from apps.affiliate.services import AffiliateService
from .models import Plan, Subscription, Payment, Invoice, PaymentGatewayConfig

logger = logging.getLogger(__name__)


class BillingService:
    @classmethod
    @transaction.atomic
    def activate_subscription_and_grant_credits(cls, payment: Payment) -> Subscription:
        """
        Activates or extends a subscription, atomically grants credits to user wallet,
        generates an official invoice, and triggers affiliate commission calculation.
        """
        # Lock user and payment
        payment = Payment.objects.select_for_update().get(id=payment.id)
        user = ApplicationUser.objects.select_for_update().get(id=payment.user_id)
        plan = payment.plan

        if not plan:
            raise ValueError("Payment is missing an associated Plan.")

        # Update Payment status
        payment.status = 'Completed'
        payment.save(update_fields=['status'])

        # Calculate subscription dates
        now = timezone.now()
        existing_sub = Subscription.objects.filter(
            user=user,
            plan=plan,
            status='active',
            end_date__gt=now
        ).order_by('-end_date').first()

        duration = timedelta(days=plan.duration_days)
        if existing_sub:
            # Extend existing active subscription
            start_date = existing_sub.start_date
            end_date = existing_sub.end_date + duration
            existing_sub.end_date = end_date
            existing_sub.save(update_fields=['end_date'])
            subscription = existing_sub
        else:
            # Create new subscription
            start_date = now
            end_date = now + duration
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                status='active'
            )

        # Link subscription to payment
        payment.subscription = subscription
        payment.save(update_fields=['subscription'])

        # Grant credits to user wallet atomically
        user.add_credits(
            standard_amount=plan.standard_credits,
            premium_amount=plan.premium_credits
        )

        # Generate Invoice
        inv_number = f"INV-{now.strftime('%Y%m')}-{payment.id:05d}"
        Invoice.objects.get_or_create(
            payment=payment,
            defaults={
                'user': user,
                'invoice_number': inv_number,
                'subtotal': payment.amount,
                'tax': Decimal('0.00'),
                'fixed_fee': Decimal('0.00'),
                'total': payment.amount,
                'currency': payment.currency,
            }
        )

        # Trigger Affiliate Commission processing
        try:
            AffiliateService.process_payment_commission(payment)
        except Exception as e:
            logger.error(f"Error processing affiliate commission for payment {payment.id}: {e}")

        logger.info(f"Subscription {subscription.id} activated for user {user.username}. Credits added: {plan.standard_credits} std, {plan.premium_credits} prem.")
        return subscription


def http_post_json(url: str, headers: dict, data, auth_tuple=None, timeout=10) -> tuple[int, dict]:
    req = urllib.request.Request(url, method='POST')
    for k, v in headers.items():
        req.add_header(k, v)
    if auth_tuple:
        import base64
        cred = base64.b64encode(f"{auth_tuple[0]}:{auth_tuple[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")
    
    body = json.dumps(data).encode('utf-8') if isinstance(data, dict) else (data.encode('utf-8') if isinstance(data, str) else b'')
    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as response:
            res_body = response.read().decode('utf-8')
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(res_body)
        except Exception:
            return e.code, {"error": res_body}
    except Exception as e:
        logger.error(f"HTTP request error to {url}: {e}")
        return 500, {"error": str(e)}


class PaymobService:
    @classmethod
    def get_config(cls) -> PaymentGatewayConfig | None:
        return PaymentGatewayConfig.objects.filter(provider__iexact='paymob', is_active=True).first()

    @classmethod
    def initiate_payment(cls, user, plan: Plan, method: str = 'card', return_host: str = '') -> dict:
        config = cls.get_config()
        currency = 'EGP'
        amount = plan.price_egp
        if amount <= Decimal('0.00'):
            amount = plan.price_usd

        # Create pending payment record
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            currency=currency,
            method=f"paymob_{method}",
            status='Pending',
            payment_id=f"PMOB-{uuid.uuid4().hex[:12].upper()}"
        )

        # If Paymob API credentials exist and not in mock mode, call Paymob Intention API
        if config and config.secret_key and not config.secret_key.startswith('mock_') and not config.secret_key.startswith('test_'):
            try:
                extra = config.extra_config or {}
                integration_id = extra.get('card_integration_id') if method == 'card' else extra.get('wallet_integration_id')
                amount_cents = int(amount * 100)
                
                payload = {
                    "amount": amount_cents,
                    "currency": currency,
                    "payment_methods": [int(integration_id)] if integration_id else [],
                    "billing_data": {
                        "first_name": user.first_name or user.username,
                        "last_name": user.last_name or "NexMedia",
                        "email": user.email or "billing@nexmedia.io",
                        "phone_number": getattr(user, 'phone_number', '+201000000000') or '+201000000000',
                        "country": "EG"
                    },
                    "special_reference": f"PM_{payment.id}_{timezone.now().timestamp()}",
                    "redirection_url": f"{return_host}/billing/success/?payment_id={payment.id}",
                }
                
                status_code, data = http_post_json(
                    "https://accept.paymob.com/v1/intention/",
                    headers={
                        "Authorization": f"Token {config.secret_key}",
                        "Content-Type": "application/json"
                    },
                    data=payload,
                    timeout=10
                )
                if status_code in [200, 201]:
                    client_secret = data.get("client_secret")
                    if client_secret:
                        checkout_url = f"https://accept.paymob.com/unifiedcheckout/?publicKey={config.public_key}&clientSecret={client_secret}"
                        return {"success": True, "checkout_url": checkout_url, "payment_id": payment.id}
            except Exception as e:
                logger.error(f"Paymob API Error: {e}")

        # Fallback to Sandbox / Mock Checkout View for seamless immediate testing
        mock_url = f"/billing/mock-checkout/?payment_id={payment.id}&gateway=paymob"
        return {"success": True, "checkout_url": mock_url, "payment_id": payment.id, "is_mock": True}

    @classmethod
    def verify_hmac(cls, data: dict, received_hmac: str) -> bool:
        config = cls.get_config()
        if not config:
            return False
        extra = config.extra_config or {}
        hmac_secret = extra.get('hmac_secret', config.secret_key or '')
        if not hmac_secret:
            return True  # If no hmac configured, allow in development

        # Concatenate Paymob HMAC keys in standard order
        keys = [
            "amount_cents", "created_at", "currency", "error_occured",
            "has_parent_transaction", "id", "integration_id", "is_3d_secure",
            "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
            "is_voided", "order", "owner", "pending", "source_data_pan",
            "source_data_sub_type", "source_data_type", "success"
        ]
        concatenated = "".join([str(data.get(k, '')) for k in keys])
        calculated_hmac = hmac.new(
            hmac_secret.encode('utf-8'),
            concatenated.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(calculated_hmac, received_hmac)


class PayPalService:
    @classmethod
    def get_config(cls) -> PaymentGatewayConfig | None:
        return PaymentGatewayConfig.objects.filter(provider__iexact='paypal', is_active=True).first()

    @classmethod
    def initiate_payment(cls, user, plan: Plan, return_host: str = '') -> dict:
        config = cls.get_config()
        currency = 'USD'
        amount = plan.price_usd

        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            currency=currency,
            method='paypal',
            status='Pending',
            payment_id=f"PP-{uuid.uuid4().hex[:12].upper()}"
        )

        # If live credentials configured, call PayPal Orders v2 API
        if config and config.secret_key and not config.secret_key.startswith('mock_') and not config.secret_key.startswith('test_'):
            try:
                extra = config.extra_config or {}
                api_base = extra.get('api_base', 'https://api-m.sandbox.paypal.com')
                
                # Get Access Token
                auth_status, auth_data = http_post_json(
                    f"{api_base}/v1/oauth2/token",
                    headers={"Accept": "application/json", "Accept-Language": "en_US", "Content-Type": "application/x-www-form-urlencoded"},
                    data="grant_type=client_credentials",
                    auth_tuple=(config.public_key, config.secret_key),
                    timeout=10
                )
                if auth_status == 200:
                    token = auth_data.get("access_token")
                    
                    order_payload = {
                        "intent": "CAPTURE",
                        "purchase_units": [{
                            "reference_id": f"PAYMENT_{payment.id}",
                            "description": f"Subscription: {plan.name}",
                            "amount": {
                                "currency_code": currency,
                                "value": f"{amount:.2f}"
                            }
                        }],
                        "application_context": {
                            "return_url": f"{return_host}/billing/success/?payment_id={payment.id}&gateway=paypal",
                            "cancel_url": f"{return_host}/billing/cancel/?payment_id={payment.id}",
                            "brand_name": "NexMedia Royal Studio",
                            "user_action": "PAY_NOW"
                        }
                    }
                    
                    order_status, order_data = http_post_json(
                        f"{api_base}/v2/checkout/orders",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json"
                        },
                        data=order_payload,
                        timeout=10
                    )
                    if order_status in [200, 201]:
                        links = {l.get('rel'): l.get('href') for l in order_data.get('links', [])}
                        approve_url = links.get('approve')
                        if approve_url:
                            payment.payment_id = order_data.get('id', payment.payment_id)
                            payment.save(update_fields=['payment_id'])
                            return {"success": True, "checkout_url": approve_url, "payment_id": payment.id}
            except Exception as e:
                logger.error(f"PayPal API Error: {e}")

        # Fallback to Sandbox / Mock Checkout View for seamless immediate testing
        mock_url = f"/billing/mock-checkout/?payment_id={payment.id}&gateway=paypal"
        return {"success": True, "checkout_url": mock_url, "payment_id": payment.id, "is_mock": True}
