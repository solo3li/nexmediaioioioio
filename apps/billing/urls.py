from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='billing_checkout'),
    path('mock-checkout/', views.mock_checkout_view, name='billing_mock_checkout'),
    path('success/', views.payment_success_view, name='billing_success'),
    path('cancel/', views.payment_cancel_view, name='billing_cancel'),
    path('manual/<int:payment_id>/', views.manual_payment_view, name='billing_manual'),
    path('webhooks/paymob/', views.paymob_webhook_view, name='paymob_webhook'),
    path('webhooks/paypal/', views.paypal_webhook_view, name='paypal_webhook'),
    path('invoices/', views.invoices_list_view, name='invoices_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
]
